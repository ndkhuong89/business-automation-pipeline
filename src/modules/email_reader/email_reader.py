import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime, timedelta

from src.config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, ATTACHMENT_DIR
from src.shared.logger import logger
from src.shared.db import is_email_processed, save_processed_email, save_attachment_record
from src.modules.email_reader.email_classifier import classify_email

ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)

def decode_email_header(value):
    if not value:
        return ""

    decoded_parts = decode_header(value)
    result = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part

    return result


def extract_attachment_names(msg):
    attachment_names = []

    if not msg.is_multipart():
        return attachment_names

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))

        if "attachment" not in content_disposition:
            continue

        filename = part.get_filename()

        if not filename:
            continue

        decoded_name = decode_email_header(filename)

        attachment_names.append(decoded_name)

    return attachment_names


def save_attachments(msg, email_uid):
    saved_files = []

    if not msg.is_multipart():
        return saved_files

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))

        if "attachment" not in content_disposition:
            continue

        filename = part.get_filename()

        if not filename:
            continue

        original_name = decode_email_header(filename)

        safe_filename = f"{email_uid}_{original_name}"

        filepath = ATTACHMENT_DIR / safe_filename

        with open(filepath, "wb") as f:
            f.write(part.get_payload(decode=True))

        save_attachment_record(
            email_uid=email_uid,
            original_name=original_name,
            stored_path=str(filepath)
        )

        logger.info(f"Attachment saved: {filepath}")

        saved_files.append(str(filepath))

    return saved_files


def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain":
                payload = part.get_payload(decode=True)

                if payload:
                    charset = part.get_content_charset() or "utf-8"

                    return payload.decode(charset, errors="ignore")

    else:
        payload = msg.get_payload(decode=True)

        if payload:
            charset = msg.get_content_charset() or "utf-8"

            return payload.decode(charset, errors="ignore")

    return ""


def process_email(msg, email_uid):
    subject = decode_email_header(msg.get("Subject"))
    sender = decode_email_header(msg.get("From"))
    email_body = extract_email_body(msg)
    
    email_type = classify_email(subject, sender, email_body)
    logger.info(f"Email type: {email_type}")

    if email_type != "ORDER":
        logger.info("Skipped non-order email")
        return

    attachment_names = extract_attachment_names(msg)
    saved_files = save_attachments(msg, email_uid)

    logger.info("=" * 50)
    logger.info(f"Processing email UID: {email_uid}")
    logger.info(f"Subject: {subject}")
    logger.info(f"From: {sender}")
    logger.info(f"Attachments: {attachment_names}")
    logger.info(f"Saved files: {saved_files}")
    logger.info(f"Email body preview: {email_body[:200]}")

    # TODO:
    # parse excel/pdf
    # automation workflow

    save_processed_email(
        email_uid=email_uid,
        subject=subject,
        sender=sender,
        attachment_names=", ".join(attachment_names),
        email_body=email_body
    )

    logger.info(f"Email UID saved: {email_uid}")


def run():
    logger.info("Connecting to email server...")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)

    try:
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        logger.info("Login successful")

        mail.select("inbox")

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        since_date = yesterday.strftime("%d-%b-%Y")
        status, messages = mail.uid("search", None, f'(SINCE "{since_date}")')
        #status, messages = mail.uid("search", None, "ALL")

        if status != "OK":
            logger.error("Failed to search emails")
            return

        email_uids = messages[0].split()

        logger.info(f"Total emails found: {len(email_uids)}")

        for uid in email_uids:
            email_uid = uid.decode()

            if is_email_processed(email_uid):
                logger.info(f"Skipping processed email UID: {email_uid}")
                continue

            status, msg_data = mail.uid("fetch", uid, "(RFC822)")

            if status != "OK":
                logger.warning(f"Failed to fetch email UID: {email_uid}")
                continue

            raw_email = msg_data[0][1]

            msg = email.message_from_bytes(raw_email)

            process_email(msg, email_uid)

    except Exception as e:
        logger.exception(f"Email processing failed: {e}")

    finally:
        mail.logout()

        logger.info("Disconnected from email server")


if __name__ == "__main__":
    run()