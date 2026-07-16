import cv2

from core.config import constants


class InputHandler:
    def __init__(self, facade, button_zone, on_board_click):
        self.facade = facade
        self.button_zone = button_zone
        self.on_board_click = on_board_click

    # --- ADD THIS METHOD ---
    def handle_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 1. Check for Game Over "New Game" button (250, 500, 300, 100)
            if self.facade._runner.status.game_over:
                if 250 <= x <= 550 and 500 <= y <= 600:
                    print("New Game button clicked!")
                    self.facade.reset_game()
                    return

            # 2. Check for "Switch Turn" button
            x1, y1, x2, y2 = self.button_zone
            if x1 <= x <= x2 and y1 <= y <= y2:
                print("Switch turn button clicked")
                self.facade.process_move("switch_turn")
                return

            # 3. Check for Board click
            row, col = self.facade.mapper.pixel_to_grid(x, y)
            if 0 <= row < constants.GRID_SIZE and 0 <= col < constants.GRID_SIZE:
                self.on_board_click(row, col)