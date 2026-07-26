import asyncio
from src.application.bootstrap import run_client_application
from src.GUI.portal_window import show_gui_home_screen
from src.utils.logger.logger import setup_logger

logger = setup_logger("MainRoom", "client_activity.log")


if __name__ == "__main__":
    try:
        asyncio.run(run_client_application(
            use_gui_auth=True,
            gui_auth_callback=show_gui_home_screen
        ))
    except Exception:
        logger.exception("Fatal error occurred in main room execution loop.")