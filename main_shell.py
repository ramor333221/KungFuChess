import asyncio
from src.application.bootstrap import run_client_application
from src.utils.logger.logger import setup_logger

logger = setup_logger("MainShell", "client_activity.log")

if __name__ == "__main__":
    try:
        asyncio.run(run_client_application())
    except Exception:
        logger.exception("Fatal error occurred in main execution loop.")