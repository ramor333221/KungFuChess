import cv2
import time
from pathlib import Path
import core.config.constants as constants
from utils.animation_manager import AnimationManager
from utils.img import Img


class BoardController:
    def __init__(self, facade, board_path: str):
        self.facade = facade
        self.board_base = Img().read(board_path)
        self.piece_animations = {}
        self.root_path = Path(__file__).resolve().parent.parent.parent

        # Load animations
        self._load_all_animations()

        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.handle_click)

    def _load_all_animations(self):
        base_path = self.root_path / "piece_mine"
        if not base_path.exists():
            return

        for piece_folder in base_path.iterdir():
            if piece_folder.is_dir():
                states_path = piece_folder / "states" / "idle"
                if states_path.exists():
                    self.piece_animations[piece_folder.name] = AnimationManager(states_path)

    def render(self):
        # 1. Start with a fresh copy of the board image
        display_img = self.board_base.copy()

        # 2. Get time in milliseconds using standard Python
        current_time = int(time.time() * 1000)

        board_matrix = self.facade.get_board_data()

        for row in range(8):
            for col in range(8):
                piece_code = board_matrix[row][col]
                if piece_code == constants.EMPTY_CELL:
                    continue

                anim = self.piece_animations.get(piece_code)
                if anim:
                    # 3. Retrieve frame from your AnimationManager
                    frame = anim.get_current_frame(current_time)

                    # 4. Get pixel center coordinates
                    x, y = self.facade.mapper.grid_to_pixel_center(row, col)

                    # 5. Draw using OpenCV
                    # Assuming frame.draw_on is a custom method, ensure it takes cv2 image
                    frame.draw_on(display_img, x - 25, y - 25)

        # 6. Show the final composed image
        cv2.imshow("Main Board", display_img)

    def handle_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Use your mapper to get grid coordinates
            col, row = self.facade.mapper.pixel_to_grid(x, y)

            # Send a structured command: "click row col"
            move_cmd = f"click {row} {col}"

            if hasattr(self.facade, 'process_move'):
                self.facade.process_move(move_cmd)

    def run(self):
            while True:
                self.render()
                if cv2.waitKey(1) == ord('q'):
                    break
            cv2.destroyAllWindows()