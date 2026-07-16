import cv2
import time
import core.config.constants as constants
from utils.img import Img


class Renderer:
    def __init__(self, facade):
        self.facade = facade
        self.dest_wrapper = Img()

    def render(self, base_img, piece_animations, selected_square):
        # Create canvas with extra space on the right for UI
        canvas = cv2.copyMakeBorder(base_img, 0, 0, 0, 300,
                                    cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
        if canvas.shape[2] == 3:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)

        board_w = base_img.shape[1]

        # 1. Draw dynamic board pieces
        self._draw_board(canvas, piece_animations, selected_square)

        # 2. Draw UI (Score, Turn, Game Over)
        self._draw_ui(canvas, board_w)

        return canvas

    def _draw_ui(self, canvas, board_w):
        status = self.facade._runner.status

        # 1. Sidebar Background
        cv2.rectangle(canvas, (board_w, 0), (canvas.shape[1], canvas.shape[0]), (40, 40, 40), -1)

        # 2. Turn Indicator
        turn_text = f"Turn: {'White' if status.current_turn == 0 else 'Black'}"
        cv2.putText(canvas, turn_text, (board_w + 20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 3. Dynamic Scores
        cv2.putText(canvas, "SCORES", (board_w + 20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 0), 2)

        w_score = status.scores.get(constants.PLAYER_WHITE, 0)
        b_score = status.scores.get(constants.PLAYER_BLACK, 0)

        cv2.putText(canvas, f"White: {w_score}", (board_w + 20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(canvas, f"Black: {b_score}", (board_w + 20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # 4. Switch Turn Button
        btn_x, btn_y, btn_w, btn_h = board_w + 50, 200, 200, 50
        cv2.rectangle(canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (100, 100, 100), -1)
        cv2.putText(canvas, "Switch Turn", (btn_x + 30, btn_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 5. Game Over Overlay
        if status.game_over:
            # Darken the board
            overlay = canvas.copy()
            cv2.rectangle(overlay, (0, 0), (canvas.shape[1], canvas.shape[0]), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, canvas, 0.5, 0, canvas)

            # Draw "GAME OVER" Text
            cv2.putText(canvas, "GAME OVER", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.putText(canvas, f"Winner: {status.winner}", (150, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

            # Draw "New Game" Button
            btn_nx, btn_ny, btn_nw, btn_nh = 250, 500, 300, 100
            cv2.rectangle(canvas, (btn_nx, btn_ny), (btn_nx + btn_nw, btn_ny + btn_nh), (255, 255, 255), -1)
            cv2.putText(canvas, "New Game", (btn_nx + 60, btn_ny + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)

    def _draw_board(self, canvas, piece_animations, selected_square):
        board_matrix = self.facade.get_board_data()
        current_time = int(time.time() * 1000)
        status = self.facade._runner.status

        cell_size = self.facade.mapper.cell_size
        piece_size = int(cell_size * 0.8)

        # Draw Valid Move Highlights
        if selected_square:
            valid_moves = self.facade.get_valid_moves(*selected_square)
            for row, col in valid_moves:
                cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)
                cv2.circle(canvas, (cx, cy), cell_size // 4, (0, 255, 0), -1)

        # Draw Pieces
        for row in range(constants.GRID_SIZE):
            for col in range(constants.GRID_SIZE):
                piece_code = board_matrix[row][col]
                if piece_code and piece_code != constants.EMPTY_CELL:
                    anim = piece_animations.get(piece_code)
                    if anim:
                        state = getattr(status, 'piece_states', {}).get((row, col), "idle")
                        anim.set_state(state)
                        frame = anim.get_current_frame(current_time)

                        if frame and hasattr(frame, 'img'):
                            resized = cv2.resize(frame.img, (piece_size, piece_size))
                            cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)
                            y1, x1 = cy - piece_size // 2, cx - piece_size // 2

                            # Blend with alpha if available
                            if resized.shape[2] == 4:
                                alpha = resized[:, :, 3] / 255.0
                                for c in range(3):
                                    canvas[y1:y1 + piece_size, x1:x1 + piece_size, c] = \
                                        alpha * resized[:, :, c] + (1 - alpha) * canvas[y1:y1 + piece_size,
                                                                                 x1:x1 + piece_size, c]
                            else:
                                canvas[y1:y1 + piece_size, x1:x1 + piece_size] = resized