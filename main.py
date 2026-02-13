import json
import os
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import date, timedelta
import sys
import requests

try:
    with open("/run/secrets/config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    # Fallback to environment variable
    config_env = os.getenv("CONFIG_JSON")
    if config_env:
        config = json.loads(config_env)
    else:
        print("ERROR: No config found. Use Docker secrets or CONFIG_JSON env var.")
        sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in config.json - {e}")
    sys.exit(1)

city: str = config["city"]
city_click: str = city + " - gmina: " + city
destination: str = config["destination"]
HEALTHCHECK_URL: str = config["healthcheck_url"]

date_lookup: str = (date.today() + timedelta(days=1)).strftime('%d.%m.%Y')


def run(playwright: Playwright) -> None:
    browser = None
    context = None
    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://pgedystrybucja.pl/wylaczenia/planowane-wylaczenia")
        page.get_by_role("button", name="Akceptuję").click()
        page.get_by_role("button", name=date_lookup).click()
        page.get_by_role("textbox", name="Miejscowość").click()
        page.get_by_role("textbox", name="Miejscowość").fill(city)
        page.get_by_text(city_click).click()
        page.get_by_role("button", name="Szukaj").click()

        # loop through page contents and see if destination street is listed in outage panel
        locator = page.get_by_text(destination)
        count = locator.count()
        found = False
        for i in range(count):
            if locator.nth(i).is_visible():
                found = True
                break

        if found:
            print(f"SUCCESS: found '{destination}'")
            requests.get(f"{HEALTHCHECK_URL}/fail", timeout=10)
        else:
            print(f"FAIL: '{destination}' not found")
            requests.get(HEALTHCHECK_URL, timeout=10)

    except PlaywrightTimeoutError as e:
        print(f"ERROR: Page element timed out - {e}")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        sys.exit(3)
    finally:
        if context:
            context.close()
        if browser:
            browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
