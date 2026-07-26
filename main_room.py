import asyncio
from pathlib import Path

from config.constants import ASSETS_PATH, DEFAULT_ELO, DEFAULT_WS_URI
from src.GUI.portal_window import show_gui_home_screen
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient
from config import constants


async def main():
    """Main asynchronous entry point with clean authentication delegation and error handling."""
    action_type, username, room_name, room_password, user_password = show_gui_home_screen()

    if action_type == constants.ACTION_CANCEL:
        return

    auth = AuthHandler()
    user_info = auth.authenticate_or_register(username, user_password, default_elo=DEFAULT_ELO)

    resolved_username = user_info['username']
    user_elo = user_info['elo']

    network_client = GameNetworkClient(username=resolved_username, room_name=room_name)

    facade = EngineFacade(
        board_path=str(ASSETS_PATH) if ASSETS_PATH.exists() else None,
        db_manager=None,
        username=resolved_username,
        network_client=network_client
    )
    facade.room_name = room_name
    facade.password = room_password

    try:
        await facade.connect_to_server(DEFAULT_WS_URI, elo=user_elo)
    except Exception as e:
        print(f"Connection failed: {e}. Please check if the server is running.")
        return

    controller = BoardController(facade, board_path=None)

    await controller.start_game_when_matched()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        import traceback
        traceback.print_exc()