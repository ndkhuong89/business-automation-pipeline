import sqlite3
from pathlib import Path
from src.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_uid TEXT UNIQUE,
            subject TEXT,
            sender TEXT,
            attachment_names TEXT,
            email_body TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_uid TEXT,
            original_name TEXT,
            stored_path TEXT,
            status TEXT DEFAULT 'PENDING',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            customer_name TEXT,
            phone TEXT,
            shipping_address TEXT,
            status TEXT,
            has_issues INTEGER DEFAULT 0,
            issue_count INTEGER DEFAULT 0,
            cs_note TEXT,
            playright_note TEXT,
            attachment_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            playright_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            report_status INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            row_number INTEGER,
            product_sku TEXT,
            product_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            is_valid INTEGER,
            errors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_order(order, attachment_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO orders (
            order_id,
            customer_name,
            phone,
            shipping_address,
            status,
            has_issues,
            issue_count,
            cs_note,
            attachment_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order["order_id"],
        order["customer_name"],
        order["phone"],
        order["shipping_address"],
        order["status"],
        int(order["has_issues"]),
        len(order["issues"]),
        order["cs_note"],
        attachment_id
    ))

    conn.commit()
    conn.close()


def save_order_items(order):
    conn = get_connection()

    cursor = conn.cursor()

    for item in order["items"]:

        cursor.execute("""
            INSERT INTO order_items (
                order_id,
                row_number,
                product_sku,
                product_name,
                quantity,
                unit_price,
                total_amount,
                is_valid,
                errors
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order["order_id"],
            item["row_number"],
            item["product_sku"],
            item["product_name"],
            str(item["quantity"]),
            str(item["unit_price"]),
            str(item["total_amount"]),
            int(item["is_valid"]),
            ", ".join(item["errors"])
        ))

    conn.commit()
    conn.close()


def get_next_pending_attachment():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, stored_path
        FROM attachments
        WHERE status = 'PENDING'
        ORDER BY id ASC
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    return row


def update_attachment_status(
    attachment_id,
    status,
    error_message=None
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attachments
        SET
            status = ?,
            error_message = ?,
            processed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status,
        error_message,
        attachment_id
    ))

    conn.commit()
    conn.close()


def is_email_processed(email_uid):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM processed_emails WHERE email_uid = ?",
        (email_uid,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def save_processed_email(
    email_uid,
    subject,
    sender,
    attachment_names,
    email_body
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO processed_emails (
            email_uid,
            subject,
            sender,
            attachment_names,
            email_body
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        email_uid,
        subject,
        sender,
        attachment_names,
        email_body
    ))

    conn.commit()
    conn.close()

def save_attachment_record(email_uid, original_name, stored_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attachments (
            email_uid,
            original_name,
            stored_path,
            status
        )
        VALUES (?, ?, ?, 'PENDING')
    """, (email_uid, original_name, stored_path))

    conn.commit()
    conn.close()

def mark_attachment_processed(file_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attachments
        SET status = 'PROCESSED',
            processed_at = CURRENT_TIMESTAMP
        WHERE stored_path = ?
    """, (file_path,))

    conn.commit()
    conn.close()

def mark_report_sent(order_ids):
    conn = get_connection()
    cur = conn.cursor()

    cur.executemany(
        """
        UPDATE orders
        SET report_status = 1
        WHERE order_id = ?
        """,
        [(oid,) for oid in order_ids]
    )

    conn.commit()

def mark_report_sent_new(order_ids):

    if not order_ids:
        return

    conn = get_connection()
    cur = conn.cursor()

    placeholders = ",".join(["?"] * len(order_ids)) #["?", "?", "?", "?", "?"]

    sql = f"""
        UPDATE orders
        SET report_status = 1
        WHERE order_id IN ({placeholders})
    """

    cur.execute(sql, order_ids)

    conn.commit()
    
def get_report_summary():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT
            status,
            COUNT(*) as total
        FROM orders
        WHERE DATE(created_at) = DATE('now')
        AND report_status = 0
        GROUP BY status
    """)

    rows = cur.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


def get_manual_review_orders():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""

        SELECT

            o.order_id,
            o.status,
            o.cs_note,
            o.playright_note,

            pe.sender,
            pe.subject,

            a.original_name

        FROM orders o

        LEFT JOIN attachments a
            ON o.attachment_id = a.id

        LEFT JOIN processed_emails pe
            ON a.email_uid = pe.email_uid

        WHERE report_status = 0
            AND (o.has_issues = 1 OR o.status = 'FAILED')
            AND DATE(o.created_at) = DATE('now')

        ORDER BY o.created_at DESC

    """)

    rows = cur.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]