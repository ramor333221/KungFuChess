import asyncio
from pathlib import Path

from DB.db_manager import DBManager
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade


async def main():
    """Main asynchronous entry point for the chess client application."""
    project_root = Path("C:/Users/User/Downloads/ChessCTD")
    assets_path = project_root / "assests" / "board.png"
    db_manager = DBManager()

    auth = AuthHandler()
    user_info = auth.login()
    if not user_info:
        print("Login failed.")
        return

    facade = EngineFacade(
        board_path=str(assets_path),
        db_manager=db_manager,
        username=user_info['username']
    )

    user_elo = user_info.get('elo', 1200)
    await facade.connect_to_server("ws://localhost:8765", elo=user_elo)

    gui = BoardController(facade, board_path=None)

    await gui.start_game_when_matched()


if __name__ == "__main__":
    asyncio.run(main())