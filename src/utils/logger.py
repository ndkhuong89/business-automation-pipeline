from loguru import logger
import sys
from pathlib import Path

# tạo thư mục logs nếu chưa có
log_dir = Path("src/logs")
log_dir.mkdir(parents=True, exist_ok=True)

logger.remove()

# log ra terminal
logger.add(
    sys.stdout,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# log ra file
logger.add(
    "src/logs/app.log",
    rotation="5 MB",
    retention="10 days",
    level="DEBUG",
    encoding="utf-8"
)