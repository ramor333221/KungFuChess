import cv2

from config import constants


class InputHandler:
    """Handles mouse click events on the board and user interface elements, removing the switch turn button."""

    def __init__(self, facade, renderer, on_board_click):
        """Initializes the input handler with facade, renderer, and click callback."""
        self.facade = facade
        self.renderer = renderer
        self.on_board_click = on_board_click

    def handle_event(self, event, x, y, flags, param):
        """Processes mouse input events on the OpenCV window without switch turn button interaction."""
        if event == cv2.EVENT_LBUTTONDOWN:
            row, col = self.facade.mapper.pixel_to_grid(x, y)
            if 0 <= row < constants.GRID_SIZE and 0 <= col < constants.GRID_SIZE:
                self.on_board_click(row, col)