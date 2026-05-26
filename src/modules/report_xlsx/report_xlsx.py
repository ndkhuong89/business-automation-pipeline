import pandas as pd
import smtplib

from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from src.config import EMAIL_ADDRESS, EMAIL_PASSWORD, DATA_OUTPUT_DIR
from src.shared.logger import logger

from src.shared.db import (
    get_report_summary,
    get_manual_review_orders,
    mark_report_sent
)

DATA_OUTPUT_DIR.mkdir(exist_ok=True)

def send_email_with_attachment(file_path):

    EMAIL_TO = EMAIL_ADDRESS

    msg = EmailMessage()
    msg["Subject"] = "Daily Business Automation Report"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_TO

    msg.set_content(
        "Attached is today's automation report."
    )

    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = file_path.name

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="octet-stream",
        filename=file_name
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        smtp.send_message(msg)


def generate_report():

    summary_data = get_report_summary()

    manual_review_data = (
        get_manual_review_orders()
    )

    summary_df = pd.DataFrame(
        summary_data
    )

    manual_review_df = pd.DataFrame(
        manual_review_data
    )
    
    if not manual_review_data:
        logger.info(f"No manual review data → skip report")
        return

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = DATA_OUTPUT_DIR / (
        f"business_report_{timestamp}.xlsx"
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        manual_review_df.to_excel(
            writer,
            sheet_name="Manual Review",
            index=False
        )

    logger.info(f"Report created: {output_file}")

    send_email_with_attachment(output_file)

    logger.info("Email sent successfully")
    
    order_ids = [
        row["order_id"]
        for row in manual_review_data
    ]

    mark_report_sent(order_ids)


if __name__ == "__main__":

    generate_report()