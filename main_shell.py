import asyncio
import logging
from pathlib import Path
from websockets.exceptions import WebSocketException

from config.constants import ASSETS_PATH, DEFAULT_ELO, DEFAULT_WS_URI
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient
from src.utils.logger.logger import setup_logger


logger = setup_logger("MainShell", "client_activity.log")


async def main():
    """Main asynchronous entry point for the CLI-based chess client application."""
    auth = AuthHandler()

    user_info = auth.login() if hasattr(auth, "login") else None
    if not user_info:
        logger.error("Login failed.")
        return

    username = user_info.get("username", "Player") if isinstance(user_info, dict) else "Player"
    user_elo = user_info.get("elo", DEFAULT_ELO) if isinstance(user_info, dict) else DEFAULT_ELO

    network_client = GameNetworkClient(username=username)

    facade = EngineFacade(
        username=username,
        network_client=network_client
    )

    try:
        await facade.connect_to_server(DEFAULT_WS_URI, elo=user_elo)
    except ConnectionRefusedError:
        logger.error("Could not connect to the game server. Is it offline?")
        return
    except WebSocketException as ws_err:
        logger.error(f"Network protocol error occurred: {ws_err}")
        return
    except Exception as unexpected_err:
        logger.exception(f"An unexpected error occurred: {unexpected_err}")
        raise

    gui = BoardController(facade, board_path=None)

    await gui.start_game_when_matched()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Fatal error occurred in main execution loop.")