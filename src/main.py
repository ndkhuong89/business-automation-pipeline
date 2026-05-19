from src.shared.db import init_db
from src.shared.logger import logger

def main():
    logger.info("Initializing database...")

    init_db()

    logger.info("Database initialized")


if __name__ == "__main__":
    main()