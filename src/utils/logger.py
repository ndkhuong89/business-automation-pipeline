from loguru import logger
import sys
import os
from pathlib import Path


# UTF-8 env (optional but ok)
os.environ["PYTHONIOENCODING"] = "utf-8"


log_dir = Path("src/logs")
log_dir.mkdir(parents=True, exist_ok=True)


logger.remove()


# console log (❌ NO encoding here)
logger.add(
    sys.stdout,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)


# file log app
logger.add(
    "src/logs/app.log",
    rotation="5 MB",
    retention="10 days",
    level="DEBUG",
    encoding="utf-8"
)


# scheduler log file
logger.add(
    "src/logs/scheduler.log",
    rotation="5 MB",
    retention="10 days",
    level="INFO",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("name") == "scheduler"
)


scheduler_logger = logger.bind(name="scheduler")