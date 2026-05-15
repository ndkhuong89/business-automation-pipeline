import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "app.db"


def get_conn():

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30
    )

    return conn


def fetch_ready_orders(limit=10):

    conn = get_conn()

    cur = conn.cursor()

    cur.execute("""
        SELECT id, order_id, customer_name, phone, shipping_address, cs_note
        FROM orders
        WHERE status = 'READY'
        LIMIT ?
    """, (limit,))

    orders = cur.fetchall()

    result = []

    for o in orders:

        _, order_id, customer, phone, address, cs_note = o

        cur.execute("""
            SELECT
                product_sku,
                product_name,
                quantity,
                unit_price,
                total_amount
            FROM order_items
            WHERE order_id = ? AND is_valid = 1
        """, (order_id,))

        items = cur.fetchall()

        result.append({
            "order_id": order_id,
            "customer_name": customer,
            "phone": phone,
            "shipping_address": address,
            "cs_note": cs_note,
            "items": items
        })

    conn.close()

    return result


def mark_done(order_id):

    conn = get_conn()

    try:

        cur = conn.cursor()

        cur.execute("""
            UPDATE orders
            SET status = 'DONE', playright_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
        """, (order_id,))

        conn.commit()

    finally:

        conn.close()


def mark_failed(order_id, error):

    conn = get_conn()

    try:

        cur = conn.cursor()

        cur.execute("""
            UPDATE orders
            SET status = 'FAILED',
                playright_note = ?
            WHERE order_id = ?
        """, (error, order_id))

        conn.commit()

    finally:

        conn.close()