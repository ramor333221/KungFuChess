import cv2
import core.config.constants as constants


class InputHandler:
    def __init__(self, facade, button_zone, on_board_click):
        self.facade = facade
        self.button_zone = button_zone  # (x1, y1, x2, y2)
        self.on_board_click = on_board_click

    def handle_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            x1, y1, x2, y2 = self.button_zone

            # Check Button Interaction
            if x1 <= x <= x2 and y1 <= y <= y2:
                print("Switch turn button clicked")
                self.facade.process_move("switch_turn")
                return

            # Check Board Interaction
            # Note: Ensure your mapper handles the coordinate (x, y) correctly
            row, col = self.facade.mapper.pixel_to_grid(x, y)
            if 0 <= row < constants.GRID_SIZE and 0 <= col < constants.GRID_SIZE:
                self.on_board_click(row, col)