from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import sys
import os
from datetime import datetime

from src.shared.logger import logger


def generate_run_id():
    return f"{datetime.now():%Y%m%d_%H%M%S}-{os.getpid()}"


def run_step(step_name: str, run_id: str):

    cmd = [sys.executable, "-m"] + step_name.split()

    logger.info(f"[RUN:{run_id}] START STEP: {step_name}")

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.stdout:
            logger.info(f"[RUN:{run_id}] {result.stdout}")

        if result.stderr:
            logger.error(f"[RUN:{run_id}] {result.stderr}")

        if result.returncode != 0:
            raise Exception(f"Step failed: {step_name}")

        logger.info(f"[RUN:{run_id}] SUCCESS STEP: {step_name}")

    except Exception as e:

        logger.exception(
            f"[RUN:{run_id}] FAILED STEP: {step_name} | {e}"
        )

        raise


def run_pipeline():

    run_id = generate_run_id()

    logger.info("============================================================")
    logger.info(f"PIPELINE STARTED | RUN_ID: {run_id}")
    logger.info("============================================================")

    try:

        run_step("src.modules.email_reader.email_reader", run_id)

        run_step("src.modules.attachment_worker.attachment_worker", run_id)

        run_step("src.modules.auto_create_order.auto_create_order", run_id) 

        logger.info(f"PIPELINE SUCCESS | RUN_ID: {run_id}")
        logger.info("=" * 100)

    except Exception as e:

        logger.exception(
            f"PIPELINE FAILED | RUN_ID: {run_id} | {e}"
        )


scheduler = BlockingScheduler()

scheduler.add_job(
    run_pipeline,
    "interval",
    minutes=5,
    next_run_time=datetime.now(),
    max_instances=1,
    coalesce=True
)

try:

    logger.info("Scheduler started...")

    scheduler.start()

except (KeyboardInterrupt, SystemExit):

    logger.info("Scheduler stopped manually")