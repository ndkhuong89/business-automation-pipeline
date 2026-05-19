from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
HEADLESS = os.getenv("HEADLESS") == "True"
LOGIN_URL = os.getenv("LOGIN_URL")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "database" / "app.db"
DATA_OUTPUT_DIR = DATA_DIR / "output"
DATA_RAW_DIR = DATA_DIR / "raw"
ATTACHMENT_DIR = DATA_DIR / "attachments"
AUTO_LOG_DIR = DATA_DIR / "auto_logs"

