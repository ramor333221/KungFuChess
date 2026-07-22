import asyncio
from pathlib import Path
from src.GUI.portal_window import show_gui_home_screen
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient
from config import constants


async def main():
    """Main asynchronous entry point with automatic background authentication."""
    action_type, username, room_name, room_password, user_password = show_gui_home_screen()

    if action_type == constants.ACTION_CANCEL:
        return

    auth = AuthHandler()
    user_info = None

    try:
        if hasattr(auth, "login_with_credentials"):
            user_info = auth.login_with_credentials(username, user_password)
        elif hasattr(auth, "login"):
            try:
                user_info = auth.login(username, user_password)
            except TypeError:
                pass

        if not user_info:
            if hasattr(auth, "register"):
                user_info = auth.register(username, user_password)
            elif hasattr(auth, "signup"):
                user_info = auth.signup(username, user_password)

            if hasattr(auth, "login_with_credentials"):
                user_info = auth.login_with_credentials(username, user_password)
            else:
                user_info = {"username": username, "elo": 1200}

        if not user_info:
            user_info = {"username": username, "elo": 1200}

    except Exception:
        user_info = {"username": username, "elo": 1200}

    project_root = Path(__file__).resolve().parent
    assets_path = project_root / "assests" / "board.png"
    resolved_username = user_info.get('username', username) if isinstance(user_info, dict) else username
    user_elo = user_info.get('elo', 1200) if isinstance(user_info, dict) else 1200

    # Initialize the network client so WebSocket communication and matching function properly
    network_client = GameNetworkClient(username=resolved_username, room_name=room_name)

    facade = EngineFacade(
        board_path=str(assets_path) if assets_path.exists() else None,
        db_manager=None,
        username=resolved_username,
        network_client=network_client
    )
    facade.room_name = room_name
    facade.password = room_password

    server_uri = getattr(constants, "SERVER_WS_URI", "ws://localhost:8765")

    await facade.connect_to_server(server_uri, elo=user_elo)

    controller = BoardController(facade, board_path=None)

    await controller.start_game_when_matched()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        import traceback
        traceback.print_exc()