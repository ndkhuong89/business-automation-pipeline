from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import sys
from datetime import datetime

from src.utils.logger import logger


def generate_run_id():

    return datetime.now().strftime("%Y%m%d_%H%M%S")


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

    logger.info("==============================")
    logger.info(f"PIPELINE STARTED | RUN_ID: {run_id}")
    logger.info("==============================")

    try:

        run_step("src.exporters.report_xlsx", run_id)

        logger.info(f"PIPELINE SUCCESS | RUN_ID: {run_id}")

    except Exception as e:

        logger.exception(
            f"PIPELINE FAILED | RUN_ID: {run_id} | {e}"
        )


scheduler = BlockingScheduler()

scheduler.add_job(
    run_pipeline,
    "interval",  
    minutes=86400,
    next_run_time=datetime.now(),
    max_instances=1,
    coalesce=True
) 

try:

    logger.info("Scheduler started...")

    scheduler.start()

except (KeyboardInterrupt, SystemExit):

    logger.info("Scheduler stopped manually")