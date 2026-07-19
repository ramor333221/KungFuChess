import cv2
from pathlib import Path

from GUI.input_handler import InputHandler
from GUI.renderer import Renderer
from config import constants
from utils.UI.animation_manager import AnimationManager
from utils.UI.img import Img


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
            renderer=self.renderer,
            on_board_click=self.handle_click
        )

        self._load_animations()
        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.input_handler.handle_event)

    def handle_click(self, row, col):
        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        turn_id = self.facade._runner.status.current_turn
        turn_map = {0: "W", 1: "B"}
        current_turn_str = turn_map.get(turn_id, "")

        if self.selected_square is None:
            if token and token != constants.EMPTY_CELL and isinstance(token, str):
                if current_turn_str in token:
                    self.selected_square = (row, col)
                else:
                    print("Not your piece!")
            return

        valid_moves = self.facade.get_valid_moves(self.selected_square[0], self.selected_square[1])

        if valid_moves and (row, col) in valid_moves:
            move_cmd = f"click {self.selected_square[0]} {self.selected_square[1]} {row} {col}"
            self.facade.process_move(move_cmd)
            self.selected_square = None
            print(f"Moved to {row}, {col}")

        elif token and isinstance(token, str) and current_turn_str in token:
            self.selected_square = (row, col)
            print("Piece re-selected")

        else:
            self.selected_square = None
            print("Selection cancelled")

    def _load_animations(self):
        base_path = Path(__file__).resolve().parent.parent / "piece_mine"
        if base_path.exists():
            for folder in base_path.iterdir():
                if folder.is_dir() and (path := folder / "states" / "idle").exists():
                    manager = AnimationManager(path)
                    size = int(self.facade.mapper.cell_size * 0.65)
                    for frame in manager.frames:
                        frame.img = cv2.resize(frame.img, (size, size), interpolation=cv2.INTER_AREA)
                    self.piece_animations[folder.name] = manager

    def handle_mouse_click(self, x: int, y: int):
        """
        Handles mouse input, distinguishing between gameplay moves
        and UI interactions (like the 'New Game' button).
        """
        status = self.facade._runner.status

        if status.game_over:
            button_x, button_y, button_w, button_h = 250, 500, 300, 100

            if button_x <= x <= (button_x + button_w) and \
                    button_y <= y <= (button_y + button_h):
                print("DEBUG: New Game button clicked.")
                self.facade.reset_game()
                return
            return

        row = y // constants.CELL_SIZE
        col = x // constants.CELL_SIZE

        if 0 <= row < constants.GRID_SIZE and 0 <= col < constants.GRID_SIZE:
            self.process_board_click(row, col)
        else:
            print(f"DEBUG: Clicked outside the board at ({x}, {y})")

    def run(self):
        last_time = cv2.getTickCount()

        while True:
            key = cv2.waitKey(1) & 0xFF

            if key == 14:  # Ctrl+N
                print("New Game triggered via Ctrl+N")
                self.facade.reset_game()
                self.selected_square = None

            if key == ord('q'):
                break

            now = cv2.getTickCount()
            delta_ms = int((now - last_time) * 1000 / cv2.getTickFrequency())
            last_time = now

            self.facade._runner.interaction_ctrl.manager.process_time_tick(delta_ms)

            canvas = self.renderer.render(
                self.board_base.img,
                self.piece_animations,
                self.selected_square
            )

            cv2.imshow("Main Board", canvas)