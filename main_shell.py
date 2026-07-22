import asyncio
from pathlib import Path

from DB.db_manager import DBManager
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade
from src.application.network.game_network_client import GameNetworkClient  # Make sure to import this


async def main():
    """Main asynchronous entry point by the shell for the chess client application."""
    project_root = Path("C:/Users/User/Downloads/ChessCTD")
    assets_path = project_root / "assests" / "board.png"
    db_manager = DBManager()

    auth = AuthHandler()
    user_info = auth.login()
    if not user_info:
        print("Login failed.")
        return

    username = user_info['username']
    user_elo = user_info.get('elo', 1200)

    # 1. Initialize the network client
    network_client = GameNetworkClient(username=username)

    # 2. Pass network_client to EngineFacade
    facade = EngineFacade(
        board_path=str(assets_path),
        db_manager=db_manager,
        username=username,
        network_client=network_client
    )

    # 3. Connect to the WebSocket server
    await facade.connect_to_server("ws://localhost:8765", elo=user_elo)

    gui = BoardController(facade, board_path=None)

    # 4. Await match start and launch the game board loop
    await gui.start_game_when_matched()


if __name__ == "__main__":
    asyncio.run(main())