"""Capture the latest cricket score from Cricbuzz with Playwright (sync API).

Usage:
    python cricbuzz_score.py              # headed (watch it work)
    python cricbuzz_score.py --headless   # headless
"""
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = "https://www.cricbuzz.com/"
# Found by inspecting the homepage in DevTools: each match in the top carousel is a
# <div class="h-fit overflow-hidden rounded shadow"> holding a link to
# /live-cricket-stream/<id>/..., a red "LIVE" badge (only when in play),
# the team names/scores and a status line ("Day 1: Stumps", "Toss delayed ...").
CARD = 'div.overflow-hidden.rounded.shadow:has(a[href*="/live-cricket-stream/"])'
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def main() -> int:
    headless = "--headless" in sys.argv
    with sync_playwright() as p:
        # Real Chrome is used because Cricbuzz returns "Access Denied" (HTTP 403)
        # to Playwright's bundled headless Chromium.
        try:
            browser = p.chromium.launch(channel="chrome", headless=headless)
        except Exception:
            browser = p.chromium.launch(headless=headless)
        # Cricbuzz also rejects the default "HeadlessChrome" user agent.
        page = browser.new_context(user_agent=UA, locale="en-IN",
                                   viewport={"width": 1366, "height": 900}).new_page()
        try:
            resp = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            if resp is not None and resp.status >= 400:
                print(f"Cricbuzz blocked the request (HTTP {resp.status}).")
                return 1
            # Wait for the score cards to render (no fixed sleep).
            page.wait_for_selector(CARD, timeout=20000)
        except PWTimeout:
            print("No score cards appeared on Cricbuzz (page slow or layout changed).")
            page.screenshot(path="score.png")
            print("saved score.png")
            browser.close()
            return 1

        cards = page.locator(CARD)
        live = cards.filter(has=page.locator("div.bg-cbLive", has_text="LIVE"))
        if live.count():
            card, note = live.first, "LIVE match:"
        else:
            card, note = cards.first, "No match is live right now - showing the latest match:"
        text = " | ".join(t.strip() for t in card.inner_text().splitlines() if t.strip())
        print(note)
        print(text)
        card.scroll_into_view_if_needed()
        card.screenshot(path="score.png")
        print("saved score.png")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
