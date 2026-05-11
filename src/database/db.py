import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")


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