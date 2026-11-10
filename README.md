# Cricbuzz live score with Playwright

Social Eagle, Week 1, Day 3, Task 1. A single script, `cricbuzz_score.py`, opens
[cricbuzz.com](https://www.cricbuzz.com/) with Playwright's sync API, waits for the
score cards to render, prints the score and saves a screenshot as `score.png`.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install playwright
playwright install chromium
```

The script drives your installed Google Chrome (`channel="chrome"`) and falls back
to Playwright's Chromium if Chrome is not found.

## Run

```bash
python cricbuzz_score.py              # headed, you can watch it work
python cricbuzz_score.py --headless   # headless
```

Example output:

```
LIVE match:
WATCH NOW | LIVE | Test | PAK | 281-5 | SL | Day 1: Stumps | SCHEDULE
saved score.png
```

## How it works

- **Selector found by inspecting the page.** Each match in the homepage carousel is a
  `div.overflow-hidden.rounded.shadow` that contains a link to `/live-cricket-stream/...`.
  The red `LIVE` badge appears only on matches in play. Teams, score and status line are
  inside the same card.
- **No fixed sleep.** `page.wait_for_selector(CARD)` continues as soon as the cards exist
  and gives up with a clear message after 20 s.
- **No live match.** If no card has the `LIVE` badge, the script says so and shows the
  latest match instead. If the page never renders, it prints a message and exits with
  code 1 instead of crashing.
- **Blocked requests.** Cricbuzz returns `Access Denied` (HTTP 403) to Playwright's
  default headless user agent, so the script sets a normal browser user agent. If it is
  still blocked, it prints the HTTP status and exits.

## Notes

- Cricbuzz changes its markup now and then. If the selector stops matching, inspect the
  page again and update `CARD`.
- `score.png` is created in the folder you run the script from (it is not stored in this repo).
  It is a screenshot of the match card whose text is printed in the terminal.
