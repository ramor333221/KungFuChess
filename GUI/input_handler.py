import cv2

from config import constants


class InputHandler:
    def __init__(self, facade, renderer, on_board_click):
        self.facade = facade
        self.renderer = renderer
        self.on_board_click = on_board_click

    def handle_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.facade._runner.status.game_over:
                if 250 <= x <= 550 and 500 <= y <= 600:
                    self.facade.reset_game()
                    return

            if (self.renderer.btn_switch_x <= x <= self.renderer.btn_switch_x + self.renderer.btn_switch_w and
                    self.renderer.btn_switch_y <= y <= self.renderer.btn_switch_y + self.renderer.btn_switch_h):
                print("Switch turn button clicked")
                self.facade.switch_player_turn()
                return

            row, col = self.facade.mapper.pixel_to_grid(x, y)
            if 0 <= row < constants.GRID_SIZE and 0 <= col < constants.GRID_SIZE:
                self.on_board_click(row, col)