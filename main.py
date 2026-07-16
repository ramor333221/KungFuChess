from GUI.ui.board_controller import BoardController
from application.engine_facade import EngineFacade

def main():
    facade = EngineFacade()
    gui = BoardController(facade, "assets/board.png")
    gui.run()


if __name__ == "__main__":
    main()