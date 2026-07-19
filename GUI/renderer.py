import time
import cv2
from config import constants
from utils.UI.img import Img


class Renderer:
    def __init__(self, facade):
        self.facade = facade
        self.dest_wrapper = Img()

        self.btn_switch_w = 200
        self.btn_switch_h = 50
        self.btn_switch_y = 600
        self.btn_switch_x = 0

    def render(self, base_img, piece_animations, selected_square):
        canvas = cv2.copyMakeBorder(base_img, 0, 0, 0, 300,
                                    cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
        if canvas.shape[2] == 3:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)

        board_w = base_img.shape[1]
        self.btn_switch_x = board_w + 50

        self._draw_board(canvas, piece_animations, selected_square)
        self._draw_ui(canvas, board_w)

        return canvas

    def _draw_ui(self, canvas, board_w):
        status = self.facade._runner.status

        cv2.rectangle(canvas, (board_w, 0), (canvas.shape[1], canvas.shape[0]), (40, 40, 40), -1)

        turn_text = f"Turn: {'White' if status.current_turn == constants.PLAYER_WHITE else 'Black'}"
        cv2.putText(canvas, turn_text, (board_w + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.putText(canvas, "SCORES", (board_w + 20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 0), 2)
        cv2.putText(canvas, f"White: {status.scores.get(constants.PLAYER_WHITE, 0)}", (board_w + 20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(canvas, f"Black: {status.scores.get(constants.PLAYER_BLACK, 0)}", (board_w + 20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.putText(canvas, "HISTORY", (board_w + 20, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 0), 2)
        column_x = {constants.PLAYER_WHITE: board_w + 10, constants.PLAYER_BLACK: board_w + 150}

        for pid in [constants.PLAYER_WHITE, constants.PLAYER_BLACK]:
            name = "White" if pid == constants.PLAYER_WHITE else "Black"
            cv2.putText(canvas, name, (column_x[pid], 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            y_offset = 240
            for move in status.command_history[pid]:
                if y_offset < 580:
                    cv2.putText(canvas, move, (column_x[pid], y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200),
                                1)
                    y_offset += 25

        cv2.rectangle(canvas, (self.btn_switch_x, self.btn_switch_y),
                      (self.btn_switch_x + self.btn_switch_w, self.btn_switch_y + self.btn_switch_h),
                      (100, 100, 100), -1)
        cv2.putText(canvas, "Switch Turn", (self.btn_switch_x + 30, self.btn_switch_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if status.game_over:
            overlay = canvas.copy()
            cv2.rectangle(overlay, (0, 0), (canvas.shape[1], canvas.shape[0]), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0, canvas)

            if status.winner == "White":
                winner_text = "White Wins!"
            elif status.winner == "Black":
                winner_text = "Black Wins!"

            cv2.putText(canvas, "GAME OVER", (board_w // 2 - 120, canvas.shape[0] // 2 - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(canvas, winner_text, (board_w // 2 - 110, canvas.shape[0] // 2 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(canvas, "Press Ctrl+N for New Game", (board_w // 2 - 150, canvas.shape[0] // 2 + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    def _draw_board(self, canvas, piece_animations, selected_square):
        board_matrix = self.facade.get_board_data()
        current_time = int(time.time() * 1000)
        status = self.facade._runner.status
        cell_size = self.facade.mapper.cell_size
        piece_size = int(cell_size * 0.8)

        if selected_square:
            valid_moves = self.facade.get_valid_moves(*selected_square)
            for row, col in valid_moves:
                cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)
                cv2.circle(canvas, (cx, cy), cell_size // 4, (0, 255, 0), -1)

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

                            if resized.shape[2] == 4:
                                alpha = resized[:, :, 3] / 255.0
                                for c in range(3):
                                    canvas[y1:y1 + piece_size, x1:x1 + piece_size, c] = \
                                        alpha * resized[:, :, c] + (1 - alpha) * canvas[y1:y1 + piece_size,
                                                                                 x1:x1 + piece_size, c]
                            else:
                                canvas[y1:y1 + piece_size, x1:x1 + piece_size] = resized