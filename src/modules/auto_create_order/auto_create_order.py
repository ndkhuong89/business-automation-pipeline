from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

from src.modules.auto_create_order.db import (
    fetch_ready_orders,
    mark_done,
    mark_failed
)

from src.config import AUTO_LOG_DIR
from src.shared.logger import logger

ERP_URL = "http://127.0.0.1:5000"
 
AUTO_LOG_DIR.mkdir(parents=True, exist_ok=True)


def take_screenshot(page, name):

    path = AUTO_LOG_DIR / f"{name}.png"

    page.screenshot(path=str(path), full_page=True)

    return path


def login(page, retry=3):

    for attempt in range(1, retry + 1):

        try:

            logger.info(f"Login attempt {attempt}")

            page.goto(f"{ERP_URL}/login", timeout=10000)

            page.fill('input[name="username"]', "admin")
            page.fill('input[name="password"]', "123456")

            page.click('button[type="submit"]')

            page.wait_for_url("**/orders/create", timeout=10000)

            logger.info("Login success")

            return

        except Exception as e:

            logger.info(f"Login failed: {e}")

            take_screenshot(page, f"login_failed_{attempt}")

            if attempt == retry:
                raise Exception("Login failed after retries")


def create_order(page, order, retry=3):

    order_id = order["order_id"]

    for attempt in range(1, retry + 1):

        try:

            logger.info(f"Create order {order_id} attempt {attempt}")

            page.goto(f"{ERP_URL}/orders/create", timeout=10000)

            page.fill('input[name="ref_order_id"]', order_id)

            page.fill(
                'input[name="customer_name"]',
                order["customer_name"]
            )

            page.fill(
                'input[name="phone"]',
                order["phone"] or ""
            )

            page.fill(
                'textarea[name="shipping_address"]',
                order["shipping_address"] or ""
            )
            page.fill(
                'textarea[name="cs_note"]',
                order["cs_note"] or ""
            )
            
            items = order["items"]

            for index, item in enumerate(items):

                sku, product_name, qty, unit_price, total = item

                if index > 0:

                    page.click("#add-product-btn")

                    page.wait_for_timeout(300)

                select = page.locator(
					'select[name="product_sku[]"]'
				).nth(index)

                select.wait_for(timeout=300)
				
                logger.info(f"Adding {sku}")

                select.select_option(value=sku)

                page.locator(
					'input[name="quantity[]"]'
				).nth(index).fill(str(qty))

            #page.click('button[type="submit"]')
            page.click("#create-order-btn")

            page.wait_for_url("**/orders", timeout=5000)

            try:

                page.locator(
                    f"text={order_id}"
                ).first.wait_for(timeout=5000)

            except TimeoutError:

                raise Exception(
                    f"Order not visible on ERP list: {order_id}"
                )

            logger.info(f"Order success {order_id}")

            return

        except Exception as e:

            logger.info(f"Order failed {order_id}: {e}")

            take_screenshot(
                page,
                f"order_failed_{order_id}_{attempt}"
            )

            if attempt == retry:

                raise Exception(
                    f"Create order failed after retries: {order_id}"
                )


def run():

    orders = fetch_ready_orders()

    if not orders:

        logger.info("No READY orders")

        return

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        try:

            login(page)

            for order in orders:

                order_id = order["order_id"]

                try:

                    logger.info(f"Processing {order_id}")

                    create_order(page, order)

                    mark_done(order_id)

                    logger.info(f"DONE {order_id}")

                except Exception as e:

                    mark_failed(order_id, str(e))

                    logger.info(f"FAILED {order_id}")

                    logger.info(e)


        finally:

            browser.close()


if __name__ == "__main__":
    run()