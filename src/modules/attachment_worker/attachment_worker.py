from src.shared.db import (
    get_next_pending_attachment,
    update_attachment_status
)

from src.modules.attachment_worker.file_validator import (
    validate_excel_file
)

from src.modules.attachment_worker.order_aggregator import (
    process_excel
)

from src.shared.logger import logger


def run():

    attachment = get_next_pending_attachment()

    if not attachment:
        logger.info("No pending attachments")
        return

    attachment_id, filepath = attachment

    logger.info(
        f"Processing attachment_id={attachment_id}"
    )

    update_attachment_status(
        attachment_id,
        "PROCESSING"
    )

    try:

        # validate file structure
        is_valid, error = validate_excel_file(
            filepath
        )

        if not is_valid:

            logger.error(
                f"Invalid file: {error}"
            )

            update_attachment_status(
                attachment_id,
                "INVALID_FORMAT",
                error
            )

            return

        # process excel + save workflow DB
        orders = process_excel(
            filepath,
            attachment_id
        )

        logger.info(
            f"Processed orders: {len(orders)}"
        )

        update_attachment_status(
            attachment_id,
            "COMPLETED"
        )

        logger.info("Attachment completed")

    except Exception as e:

        logger.exception(
            "Attachment processing failed"
        )

        update_attachment_status(
            attachment_id,
            "FAILED",
            str(e)
        )


if __name__ == "__main__":
    run()