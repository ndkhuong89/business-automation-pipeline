from playwright.sync_api import sync_playwright

from src.utils.logger import logger
from src.config import HEADLESS

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        page = browser.new_page()

        logger.info("Opening website...")

        page.goto("https://example.com")

        logger.info(f"Page title: {page.title()}")

        page.screenshot(path="data/output/example.png")

        logger.info("Screenshot saved")

        browser.close()

if __name__ == "__main__":
    run()