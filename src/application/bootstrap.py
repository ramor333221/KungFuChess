# src/application/bootstrap.py
import asyncio
from config.constants import DEFAULT_ELO, DEFAULT_WS_URI
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient
from websockets.exceptions import WebSocketException


async def run_client_application(username=None, password=None, room_name=None, room_password=None, use_gui_auth=False,
                                 gui_auth_callback=None):
    """Shared bootstrapping logic for both shell and room clients."""
    if use_gui_auth and gui_auth_callback:
        action_type, username, room_name, room_password, password = gui_auth_callback()
        from config import constants
        if action_type == constants.ACTION_CANCEL:
            return

    auth = AuthHandler()
    if username and password:
        user_info = auth.authenticate_or_register(username, password, default_elo=DEFAULT_ELO)
    else:
        user_info = auth.login() if hasattr(auth, "login") else None

    if not user_info:
        print("Login failed.")
        return

    resolved_username = user_info.get("username", "Player")
    user_elo = user_info.get("elo", DEFAULT_ELO)

    network_client = GameNetworkClient(username=resolved_username, room_name=room_name)
    facade = EngineFacade(username=resolved_username, network_client=network_client)

    if room_name:
        facade.room_name = room_name
        facade.password = room_password
    try:
        await facade.connect_to_server(DEFAULT_WS_URI, elo=user_elo)
    except (WebSocketException, ConnectionRefusedError, OSError) as e:
        print(f"Connection failed: {e}. Please check if the server is running.")
        return

    controller = BoardController(facade, board_path=None)
    await controller.start_game_when_matched()