from pathlib import Path

from src.GUI.board_controller import BoardController
from src.application.network.engine_facade import EngineFacade

if __name__ == "__main__":
    board_path = str(Path("/board.png"))
    facade_instance = EngineFacade(board_path)
    controller = BoardController(facade_instance, board_path)
    controller.run()

