import cv2
from pathlib import Path

from GUI.ui.input_handler import InputHandler
from GUI.ui.renderer import Renderer
from utils.animation_manager import AnimationManager
from utils.img import Img
import core.config.constants as constants


class BoardController:
    def __init__(self, facade, board_path: str):
        self.facade = facade
        self.board_base = Img().read(board_path)
        self.piece_animations = {}
        self.selected_square = None
        self.renderer = Renderer(facade)
        board_w = self.board_base.img.shape[1]
        self.button_zone = (board_w + 50, 50, board_w + 250, 100)

        self.input_handler = InputHandler(
            facade=facade,
            button_zone=self.button_zone,
            on_board_click=self.handle_click
        )

        self._load_animations()
        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.input_handler.handle_event)

    def handle_click(self, row, col):
        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        # Always fetch the LATEST turn from the facade
        turn_id = self.facade._runner.status.current_turn
        turn_map = {0: "W", 1: "B"}
        current_turn_str = turn_map.get(turn_id, "")

        if self.selected_square is None:
            # SELECTION LOGIC
            if token and token != constants.EMPTY_CELL and isinstance(token, str):
                if current_turn_str in token:
                    self.selected_square = (row, col)
                    print(f"Piece selected: {token}")
                else:
                    print(f"Not your piece! Current turn is {current_turn_str}")
        else:
            # MOVE LOGIC
            # Re-verify it is still the correct turn before moving
            if token and isinstance(token, str) and current_turn_str in token:
                # If we clicked another one of our own pieces, switch selection
                self.selected_square = (row, col)
            else:
                # Actually move
                move_cmd = f"click {self.selected_square[0]} {self.selected_square[1]} {row} {col}"
                print(f"Attempting move: {move_cmd}")

                # Check if the move execution was successful
                success = self.facade.process_move(move_cmd)
                self.selected_square = None

    def _load_animations(self):
        base_path = Path(__file__).resolve().parent.parent.parent / "piece_mine"
        if base_path.exists():
            for folder in base_path.iterdir():
                if folder.is_dir() and (path := folder / "states" / "idle").exists():
                    manager = AnimationManager(path)
                    size = int(self.facade.mapper.cell_size * 0.65)
                    for frame in manager.frames:
                        frame.img = cv2.resize(frame.img, (size, size), interpolation=cv2.INTER_AREA)
                    self.piece_animations[folder.name] = manager

    def run(self):
        while True:
            canvas = self.renderer.render(self.board_base.img, self.piece_animations, self.selected_square)
            cv2.imshow("Main Board", canvas)
            if cv2.waitKey(1) == ord('q'): break
        cv2.destroyAllWindows()