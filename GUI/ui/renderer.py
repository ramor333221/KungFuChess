import cv2
import time
import core.config.constants as constants
from utils.img import Img


class Renderer:
    def __init__(self, facade):
        self.facade = facade
        self.dest_wrapper = Img()

    def render(self, base_img, piece_animations, selected_square):
        canvas = cv2.copyMakeBorder(base_img, 0, 0, 0, 300,
                                    cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
        if canvas.shape[2] == 3:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)

        board_w = base_img.shape[1]
        self._draw_ui(canvas, board_w)
        self._draw_board(canvas, piece_animations, selected_square)
        return canvas

    def _draw_ui(self, canvas, board_w):
        status = self.facade._runner.status
        # Draw basic UI
        cv2.putText(canvas, f"Turn: {status.current_turn}", (board_w + 20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        y_offset = 300
        cv2.putText(canvas, f"W Score: {status.scores.get(constants.PLAYER_WHITE, 0)}",
                    (board_w + 20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(canvas, f"B Score: {status.scores.get(constants.PLAYER_BLACK, 0)}",
                    (board_w + 20, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def _draw_board(self, canvas, piece_animations, selected_square):
        board_matrix = self.facade.get_board_data()
        current_time = int(time.time() * 1000)
        status = self.facade._runner.status
        canvas_h, canvas_w = canvas.shape[:2]

        # 1. Fetch cell size and define padding
        cell_size = self.facade.mapper.cell_size
        padding = 0.8  # Pieces will be 80% of cell size
        piece_size = int(cell_size * padding)

        # Only start drawing pieces after 1s delay
        should_draw_pieces = (current_time - status.start_time) >= 1000

        # Draw Highlights (Valid Moves)
        valid_moves = self.facade.get_valid_moves(*selected_square) if selected_square else []
        for row, col in valid_moves:
            cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)
            cv2.circle(canvas, (cx, cy), cell_size // 4, (0, 255, 0), -1)

        # 2. Piece Rendering
        if should_draw_pieces:
            for row in range(constants.GRID_SIZE):
                for col in range(constants.GRID_SIZE):
                    piece_code = board_matrix[row][col]

                    if piece_code and piece_code != constants.EMPTY_CELL:
                        anim = piece_animations.get(piece_code)
                        if anim:
                            current_state = getattr(status, 'piece_states', {}).get((row, col), "idle")
                            anim.set_state(current_state)
                            frame = anim.get_current_frame(current_time)

                            if frame and hasattr(frame, 'img'):
                                # A. RESIZE: Force image to piece_size to create margins
                                resized_img = cv2.resize(frame.img, (piece_size, piece_size),
                                                         interpolation=cv2.INTER_AREA)

                                cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)
                                x = cx - (piece_size // 2)
                                y = cy - (piece_size // 2)

                                # B. CLIPPING: Calculate intersection with canvas bounds
                                y1, y2 = max(0, y), min(canvas_h, y + piece_size)
                                x1, x2 = max(0, x), min(canvas_w, x + piece_size)

                                # C. SUB-REGION: Calculate indices for the resized image
                                fy1, fy2 = y1 - y, (y2 - y)
                                fx1, fx2 = x1 - x, (x2 - x)

                                # D. DRAW: Apply to canvas
                                if x2 > x1 and y2 > y1:
                                    try:
                                        if resized_img.shape[2] == 4:
                                            # Blending with Alpha Channel
                                            alpha_s = resized_img[fy1:fy2, fx1:fx2, 3] / 255.0
                                            alpha_l = 1.0 - alpha_s
                                            for c in range(0, 3):
                                                canvas[y1:y2, x1:x2, c] = (alpha_s * resized_img[fy1:fy2, fx1:fy2, c] +
                                                                           alpha_l * canvas[y1:y2, x1:x2, c])
                                        else:
                                            # Direct copy for non-alpha images
                                            canvas[y1:y2, x1:x2] = resized_img[fy1:fy2, fx1:fx2]
                                    except Exception as e:
                                        print(f"DEBUG: Draw Error at {row},{col}: {e}")