import random
import pandas as pd

from pathlib import Path
from datetime import datetime
from src.shared.products import PRODUCTS

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_PATH = Path(
    f"data/random_orders/random_orders_{timestamp}.xlsx"
)


CUSTOMERS = [
    ("John Smith", "+1 202-555-0181", "New York, USA"),
    ("Emily Johnson", "+44 7700 900123", "London, UK"),
    ("Michael Brown", "+61 412 345 678", "Sydney, AU"),
    ("Sophia Davis", "+49 1512 3456789", "Berlin, DE"),
    ("Daniel Garcia", "+34 612 345 678", "Madrid, ES"),
    ("Anna Müller", "+49 160 1234567", "Munich, DE"),
    ("Chris Wilson", "+1 415-555-0199", "San Francisco, USA"),
]


ACTION = "CREATE_ORDER"


def corrupt(value, field):

    r = random.random()

    if r < 0.01:
        return ""

    return value


def generate_orders(num_orders=10):

    rows = []
    base = 5001
    for i in range(num_orders):
        order_id = f"ORD-{base + i}"
        #order_id = f"ORD-{datetime.now():%Y%m%d%H%M%S}-{i}"
        

        customer_name, phone, address = random.choice(CUSTOMERS)

        num_items = random.randint(2, 3)

        selected_products = random.sample(PRODUCTS, num_items)

        for product in selected_products:
            sku = product["sku"]
            name = product["name"]
            price = product["price"]

            qty = random.randint(1, 3)

            qty = corrupt(qty, "qty")

            total = None

            try:
                total = float(price) * float(qty)

            except:
                total = None

            rows.append({
                "order_id": order_id,
                "customer_name": corrupt(customer_name, "customer"),
                "phone": phone,
                "action": ACTION,
                "product_sku": sku,
                "product_name": name,
                "quantity": qty,
                "unit_price": price,
                "total_amount": total,
                "shipping_address": address,
                "priority": random.choice(["LOW", "NORMAL", "HIGH"])
            })

    return rows


def run():

    data = generate_orders(random.randint(100, 100))

    df = pd.DataFrame(data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(OUTPUT_PATH, index=False)

    print(f"Created: {OUTPUT_PATH}")
    print(f"Total rows: {len(df)}")
    print("Mode: CREATE_ORDER only, 2-3 items per order")


if __name__ == "__main__":
    run()