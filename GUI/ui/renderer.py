import cv2
import time
import core.config.constants as constants
from utils.img import Img


class Renderer:
    def __init__(self, facade):
        self.facade = facade
        self.dest_wrapper = Img()

    def render(self, base_img, piece_animations, selected_square):
        # 1. Create canvas with 300px sidebar
        canvas = cv2.copyMakeBorder(base_img, 0, 0, 0, 300,
                                    cv2.BORDER_CONSTANT, value=[0, 0, 0])
        board_w = base_img.shape[1]

        if self.facade.get_game_over_status():
            return canvas

        self._draw_ui(canvas, board_w)
        self._draw_board(canvas, piece_animations, selected_square)

        return canvas

    def _draw_ui(self, canvas, board_w):
        # Button
        cv2.rectangle(canvas, (board_w + 50, 50), (board_w + 250, 100), (200, 200, 200), -1)
        cv2.putText(canvas, "SWITCH TURN", (board_w + 80, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Status & History
        status = self.facade._runner.status
        cv2.putText(canvas, f"Turn: {status.current_turn}", (board_w + 20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        y_offset = 200
        for cmd in status.command_history[-10:]:
            cv2.putText(canvas, cmd, (board_w + 20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            y_offset += 30

    def _draw_board(self, canvas, piece_animations, selected_square):
        board_matrix = self.facade.get_board_data()
        cell_size = self.facade.mapper.cell_size
        half_cell = cell_size // 2
        current_time = int(time.time() * 1000)

        valid_moves = self.facade.get_valid_moves(*selected_square) if selected_square else []

        for row in range(constants.GRID_SIZE):
            for col in range(constants.GRID_SIZE):
                cx, cy = self.facade.mapper.grid_to_pixel_center(row, col)

                # Highlights
                if selected_square == (row, col):
                    cv2.rectangle(canvas, (cx - half_cell, cy - half_cell),
                                  (cx + half_cell, cy + half_cell), (255, 255, 0), 3)
                elif (row, col) in valid_moves:
                    cv2.circle(canvas, (cx, cy), half_cell // 2, (0, 255, 0), -1)

                # Pieces
                piece_code = board_matrix[row][col]
                if piece_code and piece_code != constants.EMPTY_CELL:
                    anim = piece_animations.get(piece_code)
                    if anim:
                        frame = anim.get_current_frame(current_time)
                        dest_x = cx - (frame.img.shape[1] // 2)
                        dest_y = cy - (frame.img.shape[0] // 2)
                        self.dest_wrapper.img = canvas
                        frame.draw_on(self.dest_wrapper, dest_x, dest_y)
                        canvas = self.dest_wrapper.img