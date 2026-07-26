import asyncio
from pathlib import Path

from DB.db_manager import DBManager
from config.constants import ASSETS_PATH, DEFAULT_ELO, DEFAULT_WS_URI
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient


async def main():
    """Main asynchronous entry point for the CLI-based chess client application."""
    db_manager = DBManager()

    auth = AuthHandler()

    user_info = auth.login() if hasattr(auth, "login") else None
    if not user_info:
        print("Login failed.")
        return

    username = user_info.get("username", "Player") if isinstance(user_info, dict) else "Player"
    user_elo = user_info.get("elo", DEFAULT_ELO) if isinstance(user_info, dict) else DEFAULT_ELO

    network_client = GameNetworkClient(username=username)

    facade = EngineFacade(
        board_path=str(ASSETS_PATH) if ASSETS_PATH.exists() else None,
        db_manager=db_manager,
        username=username,
        network_client=network_client
    )

    try:
        await facade.connect_to_server(DEFAULT_WS_URI, elo=user_elo)
    except Exception as e:
        print(f"Connection failed: {e}. Please check if the server is running.")
        return

    gui = BoardController(facade, board_path=None)

    await gui.start_game_when_matched()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        import traceback

        traceback.print_exc()