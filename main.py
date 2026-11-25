#!/usr/bin/env python3
"""Wednesday 25 November 2026 in one image.

A dense newspaper front page drawn from scratch in pure Python stdlib:
own raster canvas, own 5x7 bitmap font, own PNG encoder. No PIL, no network.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Deterministic: two runs write byte-identical output.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------- canvas
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 28)
BLUE = (28, 58, 110)
SKY = (16, 32, 68)
GOLD = (201, 138, 20)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg[0] for _ in range(w * h))
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = (yy * self.w + xx) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, c, t=2):
        for ox in range(-(t // 2), t // 2 + 1):
            for oy in range(-(t // 2), t // 2 + 1):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, c)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.put(xx, yy, c)
                else:
                    if r * r - r <= d <= r * r + r:
                        self.put(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0) if y1 != y0 else 0
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.put(x, y, c)

    def text(self, x, y, s, c, scale=1):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for ry, row in enumerate(g):
                for rx, bit in enumerate(row):
                    if bit == '#':
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def text_centre(self, x, y, w, s, c, scale=1):
        tw = self.text_w(s, scale)
        self.text(x + (w - tw) // 2, y, s, c, scale)

    def wrap(self, x, y, w, s, c, scale=1, lh=None):
        """Word-wrap text into box of width w; returns y after last line."""
        if lh is None:
            lh = 8 * scale + 2
        maxw = w // (6 * scale)
        words = s.split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if len(trial) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        for ln in lines:
            self.text(x, y, ln, c, scale)
            y += lh
        return y


def chunk(typ, data):
    c = struct.pack('>I', len(data)) + typ + data
    c += struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    return c


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- pictures
def pic_rocket(cv, x, y, w, h):
    """Night launch: dark sky, stars, rocket on pad, flame, smoke."""
    cv.rect(x, y, w, h, SKY)
    # stars
    for (sx, sy, r) in [(12, 14, 1), (48, 30, 1), (90, 10, 2), (130, 44, 1),
                        (170, 18, 1), (210, 36, 1), (250, 12, 1), (290, 40, 1),
                        (330, 16, 1), (370, 30, 1), (400, 8, 1), (70, 60, 1),
                        (300, 60, 1), (150, 70, 1), (240, 78, 1)]:
        cv.circle(x + sx, y + sy, r, (255, 255, 255))
    # moon
    cv.circle(x + w - 52, y + 26, 14, (240, 236, 210))
    cv.circle(x + w - 56, y + 22, 12, SKY)
    # ground
    cv.rect(x, y + h - 26, w, 26, (10, 14, 26))
    cv.hline(x, y + h - 26, w, (90, 100, 130), 2)
    # pad
    cv.rect(x + w // 2 - 46, y + h - 46, 92, 20, (70, 76, 90))
    # smoke
    for (sx, sy, r) in [(w // 2 - 70, h - 40, 16), (w // 2 + 74, h - 36, 14),
                        (w // 2 - 96, h - 30, 11), (w // 2 + 96, h - 28, 10)]:
        cv.circle(x + sx, y + sy, r, (150, 155, 170))
    # flame
    cx = x + w // 2
    cv.poly([(cx - 12, y + h - 46), (cx + 12, y + h - 46),
             (cx + 5, y + h - 8), (cx, y + h - 2), (cx - 5, y + h - 8)],
            (255, 150, 30))
    cv.poly([(cx - 6, y + h - 46), (cx + 6, y + h - 46),
             (cx + 2, y + h - 16), (cx, y + h - 12), (cx - 2, y + h - 16)],
            (255, 220, 80))
    # rocket body
    by = y + 22
    cv.rect(cx - 13, by + 18, 26, 78, (240, 240, 235))
    cv.poly([(cx - 13, by + 18), (cx + 13, by + 18), (cx, by)], (214, 40, 40))
    cv.rect(cx - 13, by + 40, 26, 6, (28, 58, 110))
    cv.circle(cx, by + 58, 6, (120, 200, 240))
    cv.circle(cx, by + 58, 6, (120, 200, 240), fill=False)
    # fins
    cv.poly([(cx - 13, by + 78), (cx - 30, by + 100), (cx - 13, by + 100)],
            (178, 34, 28))
    cv.poly([(cx + 13, by + 78), (cx + 30, by + 100), (cx + 13, by + 100)],
            (178, 34, 28))
    # flag stripe
    cv.rect(cx - 13, by + 88, 26, 8, (0, 120, 60))
    cv.text(x + 10, y + h - 20, "JIUQUAN  00:18 UTC", (255, 255, 255), 1)


def pic_markets(cv, x, y, w, h):
    """Falling chart on a dark board, red line, big red arrow."""
    cv.rect(x, y, w, h, (14, 16, 20))
    # grid
    for gy in range(y + 16, y + h - 8, 18):
        cv.hline(x + 8, gy, w - 16, (38, 42, 52), 1)
    # falling line
    pts = [(x + 12, y + 18), (x + 34, y + 26), (x + 52, y + 22),
           (x + 72, y + 44), (x + 92, y + 40), (x + 112, y + 66),
           (x + 132, y + 62), (x + 152, y + 92), (x + 172, y + 104)]
    for i in range(len(pts) - 1):
        cv.thick_line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      (255, 70, 60), 3)
    # down arrow
    ax, ay = x + w - 42, y + 14
    cv.poly([(ax, ay), (ax + 10, ay), (ax + 10, ay + 14),
             (ax + 20, ay + 14), (ax + 5, ay + 28), (ax - 10, ay + 14),
             (ax, ay + 14)], (255, 70, 60))
    cv.text(x + 10, y + h - 18, "KOSPI -6%  NIKKEI -3%", (255, 120, 110), 1)


def pic_tower(cv, x, y, w, h):
    """Riyadh skyline at dusk, tallest tower with a damage mark and smoke."""
    cv.rect(x, y, w, h, (58, 34, 40))
    cv.rect(x, y + h - 34, w, 34, (30, 18, 22))
    # sun glow
    cv.circle(x + 34, y + 30, 12, (255, 170, 80))
    # skyline
    for (bx, bw, bh) in [(8, 18, 46), (30, 14, 34), (48, 20, 58),
                         (130, 16, 40), (148, 22, 62), (172, 12, 30)]:
        cv.rect(x + bx, y + h - 34 - bh, bw, bh, (24, 16, 20))
    # PIF tower (tallest, centre-right)
    tx = x + w // 2 - 12
    cv.rect(tx, y + 16, 24, h - 50, (200, 180, 120))
    cv.rect(tx + 4, y + 10, 16, 8, (200, 180, 120))
    for wy in range(y + 24, y + h - 56, 10):
        cv.hline(tx + 3, wy, 18, (120, 100, 60), 1)
    # damage mark + smoke
    cv.rect(tx + 2, y + 52, 20, 8, (40, 20, 16))
    cv.circle(tx + 26, y + 46, 7, (120, 116, 110))
    cv.circle(tx + 34, y + 38, 9, (140, 136, 128))
    cv.circle(tx + 42, y + 28, 11, (160, 156, 148))
    cv.text(x + 8, y + h - 18, "PIF TOWER  385 M", (255, 220, 180), 1)


def pic_ship(cv, x, y, w, h):
    """Cargo ship at sea under a drone, smoke rising."""
    cv.rect(x, y, w, h, (120, 170, 210))
    cv.circle(x + w - 30, y + 22, 12, (250, 240, 200))
    # sea
    cv.rect(x, y + h - 44, w, 44, (16, 70, 130))
    for wy in range(y + h - 40, y + h - 6, 9):
        for wx in range(x + 6, x + w - 10, 26):
            cv.hline(wx, wy, 14, (120, 180, 230), 2)
    # ship hull
    hx = x + 24
    cv.poly([(hx, y + h - 52), (hx + w - 48, y + h - 52),
             (hx + w - 66, y + h - 22), (hx + 14, y + h - 22)], (30, 32, 38))
    # containers
    cv.rect(hx + 14, y + h - 76, 30, 24, (178, 34, 28))
    cv.rect(hx + 48, y + h - 76, 30, 24, (28, 90, 140))
    cv.rect(hx + 82, y + h - 76, 30, 24, (201, 138, 20))
    cv.rect(hx + 116, y + h - 66, 26, 14, (60, 120, 70))
    # bridge
    cv.rect(hx + w - 66, y + h - 88, 22, 36, (220, 220, 210))
    # fire + smoke
    cv.poly([(hx + 60, y + h - 76), (hx + 74, y + h - 76),
             (hx + 67, y + h - 92)], (255, 150, 30))
    cv.circle(hx + 67, y + h - 100, 8, (90, 88, 84))
    cv.circle(hx + 74, y + h - 112, 10, (110, 108, 104))
    cv.circle(hx + 82, y + h - 126, 12, (130, 128, 122))
    # drone
    cv.circle(x + w // 2 + 30, y + 26, 3, (20, 20, 20))
    cv.hline(x + w // 2 + 22, y + 26, 16, (20, 20, 20), 1)
    cv.text(x + 8, y + 8, "SPARTA II", (255, 255, 255), 1)


def pic_gaza(cv, x, y, w, h):
    """Gaza skyline at night, smoke columns, orange glow."""
    cv.rect(x, y, w, h, (40, 36, 44))
    # glow
    cv.circle(x + w // 2, y + h - 30, 26, (255, 140, 40))
    cv.circle(x + w // 2, y + h - 30, 16, (255, 190, 90))
    # buildings
    for (bx, bw, bh) in [(6, 22, 52), (32, 16, 70), (52, 26, 44),
                         (82, 18, 62), (104, 24, 48), (132, 16, 74),
                         (152, 22, 40), (178, 14, 56)]:
        cv.rect(x + bx, y + h - 34 - bh, bw, bh, (16, 14, 16))
        for wy in range(y + h - 30 - bh, y + h - 38, 12):
            cv.rect(x + bx + 4, wy, 3, 4, (255, 200, 90))
    # smoke columns
    cv.circle(x + 60, y + 26, 9, (120, 116, 112))
    cv.circle(x + 66, y + 16, 12, (140, 136, 130))
    cv.circle(x + 150, y + 30, 8, (120, 116, 112))
    cv.circle(x + 156, y + 20, 11, (140, 136, 130))
    cv.rect(x, y + h - 34, w, 34, (10, 10, 12))
    cv.text(x + 8, y + h - 18, "GAZA CITY", (255, 220, 180), 1)


# ---------------------------------------------------------------- world map
# Coarse continent outlines in (lon, lat); equirectangular projection.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 71), (-100, 68), (-85, 66), (-80, 73),
     (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 30), (-125, 40), (-125, 49),
     (-140, 60), (-155, 58), (-168, 66)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-75, -45), (-80, -20),
     (-80, -5), (-80, 10)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 55), (28, 60), (30, 62), (30, 70), (20, 70), (12, 66),
     (5, 60), (5, 58), (-2, 50), (-5, 43), (-9, 37), (-10, 36)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11),
     (48, 0), (40, -10), (36, -18), (32, -28), (20, -35), (16, -28),
     (12, -18), (9, -2), (9, 4), (-8, 4), (-16, 12), (-17, 20), (-10, 30),
     (-6, 35)],
    # Asia
    [(30, 70), (50, 68), (70, 72), (90, 75), (110, 74), (130, 72),
     (160, 66), (178, 65), (170, 60), (158, 52), (142, 50), (140, 40),
     (130, 33), (122, 30), (115, 22), (108, 10), (100, 8), (95, 16),
     (90, 22), (80, 10), (77, 8), (72, 20), (66, 25), (60, 25), (55, 27),
     (50, 29), (48, 30), (43, 12), (40, 15), (35, 28), (30, 36), (27, 41),
     (23, 40), (20, 45), (15, 44), (10, 45), (8, 44), (3, 42), (0, 40),
     (-2, 37), (5, 37), (10, 37), (20, 40), (26, 38), (30, 36), (35, 36),
     (36, 36), (30, 42), (28, 45), (30, 46), (32, 52), (35, 55), (40, 60),
     (45, 66), (30, 70)],
    # Australia
    [(114, -22), (122, -14), (132, -12), (142, -11), (146, -19), (150, -22),
     (153, -27), (150, -37), (140, -38), (130, -32), (124, -33), (115, -35),
     (113, -25), (114, -22)],
]

PINS = [
    ("JIUQUAN", 100, 40), ("SEOUL", 127, 37), ("TOKYO", 139, 35),
    ("TAIPEI", 121, 25), ("RIYADH", 47, 25), ("GAZA", 34, 31),
    ("FINLAND", 24, 60), ("KYIV", 30, 50), ("NEW YORK", -74, 41),
    ("KATHMANDU", 85, 28), ("KUALA LUMPUR", 102, 3), ("HODEIDA", 43, 15),
]

# Label side per pin ('L' = label to the left of the pin, 'R' = right);
# crowded Europe / Middle East pins get explicit sides so labels never stack.
LABEL_SIDE = {
    "SEOUL": "L", "GAZA": "L", "KATHMANDU": "L",
    "FINLAND": "L", "RIYADH": "R", "HODEIDA": "R", "JIUQUAN": "L",
}
# Extra vertical nudge (pixels) for a few labels to clear neighbours.
LABEL_DY = {"FINLAND": -12, "KYIV": 4, "HODEIDA": 12, "TAIPEI": 2,
            "JIUQUAN": -10, "KATHMANDU": 8, "GAZA": 2}


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, (214, 228, 238))
    cv.frame(x, y, w, h, INK, 1)
    # graticule
    for gx in range(x + 40, x + w, 40):
        cv.vline(gx, y, h, (190, 205, 218), 1)
    for gy in range(y + 18, y + h, 18):
        cv.hline(x, gy, w, (190, 205, 218), 1)
    # continents
    for cont in CONTINENTS:
        pts = []
        for lon, lat in cont:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((90 - lat) / 180.0 * h)
            pts.append((px, py))
        cv.poly(pts, (96, 118, 92))
    # pins
    for name, lon, lat in PINS:
        px = x + int((lon + 180) / 360.0 * w)
        py = y + int((90 - lat) / 180.0 * h)
        cv.circle(px, py, 5, RED)
        cv.circle(px, py, 2, (255, 255, 255))
        cv.circle(px, py, 5, INK, fill=False)
        ly = py - 4 + LABEL_DY.get(name, 0)
        if LABEL_SIDE.get(name, "R") == "L":
            lx = px - 7 - len(name) * 6
        else:
            lx = px + 7
            if lx + len(name) * 6 > x + w - 4:
                lx = px - 7 - len(name) * 6
        cv.text(lx, ly, name, INK, 1)
    cv.text(x + 6, y + 4, "THE WORLD TODAY", INK, 1)


# ---------------------------------------------------------------- stories
LEADS = [
    dict(kicker="SPACE", pic=pic_rocket,
         head=["PAKISTAN'S FIRST", "ASTRONAUT IN ORBIT"],
         deck="Shenzhou-24 lifts off from Jiuquan at 00:18 UTC. Zeeshan Ali, 40, "
              "is the first Pakistani in space and the first foreign astronaut "
              "aboard China's Tiangong station. A week aboard, 90 experiments."),
    dict(kicker="MARKETS", pic=pic_markets,
         head=["AI RALLY UNWINDS:", "ASIA SELLS OFF"],
         deck="Kospi -6%, Nikkei -3%, Taiex -7%. SoftBank -16% to a 52-week low "
              "as tariff fears return. Nasdaq fell 1.5% on Tuesday; the Dow "
              "closed above 50,000 for the first time."),
    dict(kicker="RIYADH", pic=pic_tower,
         head=["HOUTHIS HIT RIYADH", "TOWER AGAIN"],
         deck="A drone strike wounds 11 at the 385 m PIF tower, the second hit "
              "in a week. The Saudi-led coalition vows a decisive reply as "
              "Houthi fire on Saudi cities goes on almost daily."),
    dict(kicker="UKRAINE", pic=pic_ship,
         head=["KYIV: WE HIT THE", "RUSSIAN SHIP"],
         deck="Zelenskiy confirms Ukraine's drone strike on the Sparta II in "
              "the Gulf of Finland. The arms-laden ship, bound for Kaliningrad, "
              "was set aflame; Norway urges caution."),
    dict(kicker="GAZA", pic=pic_gaza,
         head=["ISRAEL KILLS HAMAS", "SECURITY CHIEF"],
         deck="An airstrike in Gaza City kills Naeem Abu Nahel, 50, head of "
              "Hamas internal security. At least seven dead; Netanyahu hails "
              "Israel's long reach."),
]

MORE = [
    "HUAWEI: US jury convicts on 10 of 12 counts",
    "YEMEN: Saudi strikes kill 17 in Hodeida, 26 in Lahj",
    "S KOREA: Russian jets enter air defence zone",
    "BANGLADESH: Hasina to return home on 16 Dec",
    "MALAYSIA: 6,500 Rohingya to be sent back in Dec",
    "HEALTH: AIDS deaths 570,000 in 2025, lowest in 20 yr",
    "UAE: Bus crash toll in Ras Al Khaimah rises to 13",
    "NEPAL: Quake 5.6 hits Koshi province near Tibet",
    "DR CONGO: Military aircraft missing amid rebel claims",
    "IRAQ: Crackdown on oil smuggling under way",
    "CHINA: Shanghai party chief Chen Jining probed",
    "MALI: Leaked data on Russian deaths in Mali",
    "HOUTHIS: Threats to Saudi ports continue",
    "FORT HOOD: Hasan seeks stay of execution",
    "SARKOZY: Ex-president's corruption case to trial",
    "LIBYA: Russian ship sinking stirs frozen conflict",
    "ADEN: Houthis within 60 km; govt says city safe",
    "O'HARE: Radar fault delays flights in Chicago",
    "THANKSGIVING: Trump spares turkeys Freedom, Feathers",
    "ISRAEL AID: US envoy unsure aid ends this year",
    "GIULIANI: Trump awards Medal of Freedom",
    "SWEDEN: Parliament votes on Kristersson as PM",
    "CIA: Breach hits CIA and ODNI unclassified data",
    "UK: Public asked on age of consent change",
    "UK: Panel on nuclear test veterans' health",
    "DELL: Forecasts up after record AI server quarter",
    "NVIDIA: Shares fall 7% as lawmakers press Trump",
    "IOWA: Army to detonate 68 barrels of lead azide Wed",
    "VENEZUELA: Public debt officially $237.5bn",
    "KURDISTAN: Baghdad PM seeks more power over region",
    "TARIFFS: US set to unveil new tariffs on partners",
    "SPORT: Bellingham stunner sees Real Madrid past PSV",
    "MAN UTD: Pochettino fury at Yoro red card",
    "INDIA: Two Indians among 11 hurt in Riyadh strike",
    "IRAN: Singer Parastoo Ahmadi given 74 lashes",
    "NATO: Response to Russian nuclear satellite reports",
    "EU: Caps on Chinese hybrid EVs; budget row",
    "BULGARIA: Fiscal strains; EU report cards out",
]


def draw_lead(cv, x, y, w, h, lead, big=False):
    cv.frame(x, y, w, h, INK, 1)
    pic_w = 420 if big else 200
    lead["pic"](cv, x + 1, y + 1, pic_w, h - 2)
    tx = x + pic_w + 12
    tw = w - pic_w - 22
    ty = y + 10
    cv.text(tx, ty, lead["kicker"], RED, 1)
    ty += 14
    scale = 3 if big else 2
    for ln in lead["head"]:
        cv.text(tx, ty, ln, INK, scale)
        ty += 8 * scale + 4
    ty += 2
    cv.hline(tx, ty, tw, GREY, 1)
    ty += 8
    cv.wrap(tx, ty, tw, lead["deck"], INK, 2 if big else 1)


def main():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.text_centre(20, 14, 984, "THE WORLD IN ONE PAGE", GREY, 1)
    cv.text_centre(20, 34, 984, "WEDNESDAY 25 NOVEMBER 2026", INK, 4)
    cv.hline(20, 74, 984, RED, 3)
    cv.hline(20, 79, 984, INK, 1)
    # lead 1, full width
    draw_lead(cv, 20, 88, 984, 204, LEADS[0], big=True)
    # leads 2-5, 2x2 grid
    gx, gy = 20, 300
    gw, gh, gap = 486, 176, 12
    for i, lead in enumerate(LEADS[1:]):
        lx = gx + (i % 2) * (gw + gap)
        ly = gy + (i // 2) * (gh + gap)
        draw_lead(cv, lx, ly, gw, gh, lead)
    # world map
    my = gy + 2 * gh + gap + 8
    draw_map(cv, 20, my, 984, 140)
    # more stories
    sy = my + 140 + 10
    cv.text(20, sy, "ALSO TODAY - 38 MORE STORIES", RED, 1)
    cv.hline(20, sy + 12, 984, INK, 1)
    ly = sy + 20
    cols = [MORE[0:13], MORE[13:26], MORE[26:38]]
    for ci, col in enumerate(cols):
        cx = 20 + ci * 330
        yy = ly
        for item in col:
            cv.text(cx, yy, item, INK, 1)
            yy += 11
    # date-check strip
    fy = 990
    cv.rect(20, fy, 984, 18, INK)
    cv.text(28, fy + 5,
            "DATE CHECK: SHENZHOU-24 LAUNCHED 00:18 UTC TODAY - ASIAN MARKETS "
            "FELL THIS MORNING - 43 STORIES VERIFIED VS REUTERS, AP, BBC, XINHUA",
            (255, 255, 255), 1)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
