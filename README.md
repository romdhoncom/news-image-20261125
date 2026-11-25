[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/romdhoncom/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/romdhoncom/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# Wednesday 25 November 2026 in one image

A dense newspaper front page summing up the world's news of Wednesday
25 November 2026, drawn from scratch in pure Python stdlib — own raster
canvas, own 5x7 bitmap font, own PNG encoder. No PIL, no network.

The front page: masthead "WEDNESDAY 25 NOVEMBER 2026", five lead stories
with pictures — Shenzhou-24 launches with Pakistan's first astronaut in
orbit; Asian markets sell off as the AI rally unwinds; Houthis hit
Riyadh's tallest tower again, 11 hurt; Zelenskiy confirms Ukraine hit
the Russian ship Sparta II; Israel kills Hamas security chief Naeem Abu
Nahel in Gaza — plus a world map with 12 pins, 38 more stories, and a
date-check strip. All 43 stories verified against Reuters, AP, BBC and
Xinhua in the morning round of 25 November 2026 (round 1: the day was
still in progress, so this is the morning's news).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, ~34 KB). Two runs write byte-identical
output.
