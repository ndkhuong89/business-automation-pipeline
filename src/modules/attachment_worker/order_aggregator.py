import math
import pandas as pd

from collections import defaultdict

from src.shared.logger import logger

from src.shared.db import (
    save_order,
    save_order_items
)


REQUIRED_FIELDS = [
    "order_id",
    "customer_name",
    "product_sku",
    "product_name",
    "quantity",
    "unit_price"
]


def is_empty(value):
    if value is None:
        return True

    if isinstance(value, float) and math.isnan(value):
        return True

    return str(value).strip() == ""


def validate_row(row):
    errors = []

    # required fields
    for field in REQUIRED_FIELDS:
        if is_empty(row.get(field)):
            errors.append(f"{field}_missing")

    # quantity validation
    try:
        qty = int(row.get("quantity"))

        if qty <= 0:
            errors.append("quantity_invalid")

    except:
        errors.append("quantity_not_numeric")

    # price validation
    try:
        price = float(row.get("unit_price"))

        if price <= 0:
            errors.append("unit_price_invalid")

    except:
        errors.append("unit_price_not_numeric")

    return errors


def generate_cs_note(order):

    issues = order["issues"]

    if not issues:
        return ""

    lines = [
        "⚠ DATA VALIDATION ISSUES",
        ""
    ]

    for item in order["items"]:

        if item["is_valid"]:
            continue

        lines.append("----------------------------")
        lines.append(f"SKU: {item['product_sku']}")
        lines.append(f"Product: {item['product_name']}")
        lines.append(f"Quantity: {item['quantity']}")
        lines.append(f"Unit Price: {item['unit_price']}")
        lines.append("")

        for error in item["errors"]:
            lines.append(f"- {error}")

        lines.append("")

    lines.append("Please review before fulfillment.")

    return "\n".join(lines)


def process_excel(filepath, attachment_id):
    logger.info(f"Processing Excel: {filepath}")

    df = pd.read_excel(filepath)

    grouped_orders = defaultdict(lambda: {
        "order_id": None,
        "customer_name": None,
        "phone": None,
        "shipping_address": None,
        "items": [],
        "issues": [],
        "has_issues": False,
        "valid_item_count": 0,
        "invalid_item_count": 0,
        "status": "PENDING",
        "cs_note": ""
    })

    logger.info(f"Total rows: {len(df)}")

    for index, row in df.iterrows():

        row_number = index + 2

        row_data = row.to_dict()

        order_id = str(row_data.get("order_id")).strip()

        order = grouped_orders[order_id]

        # set order-level info once
        if not order["order_id"]:
            order["order_id"] = order_id
            order["customer_name"] = row_data.get("customer_name")
            order["phone"] = row_data.get("phone")
            order["shipping_address"] = row_data.get("shipping_address")

        errors = validate_row(row_data)

        item = {
            "row_number": row_number,
            "product_sku": row_data.get("product_sku"),
            "product_name": row_data.get("product_name"),
            "quantity": row_data.get("quantity"),
            "unit_price": row_data.get("unit_price"),
            "total_amount": row_data.get("total_amount"),
            "is_valid": len(errors) == 0,
            "errors": errors
        }

        order["items"].append(item)

        # valid row
        if not errors:
            order["valid_item_count"] += 1

        # invalid row
        else:
            order["invalid_item_count"] += 1
            order["has_issues"] = True

            for error in errors:
                order["issues"].append(
                    f"Row {row_number}: {error}"
                )

    final_orders = []

    for order in grouped_orders.values():

        # final order status
        if order["valid_item_count"] > 0:
            order["status"] = "READY"
        else:
            order["status"] = "REJECTED"

        # build CS note
        order["cs_note"] = generate_cs_note(
            order
        )

        # save workflow DB
        save_order(order, attachment_id)

        save_order_items(order)

        final_orders.append(order)

    logger.info(f"Final orders: {len(final_orders)}")

    ready_orders = [
        o for o in final_orders
        if o["status"] == "READY"
    ]

    rejected_orders = [
        o for o in final_orders
        if o["status"] == "REJECTED"
    ]

    logger.info(f"READY orders: {len(ready_orders)}")
    logger.info(f"REJECTED orders: {len(rejected_orders)}")

    return final_orders