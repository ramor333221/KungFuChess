from pathlib import Path

from GUI.board_controller import BoardController
from application.engine_facade import EngineFacade

if __name__ == "__main__":
    board_path = str(Path("C:/Users/User/Downloads/78/board.png"))
    facade_instance = EngineFacade(board_path)
    controller = BoardController(facade_instance, board_path)
    controller.run()

