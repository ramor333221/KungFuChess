from typing import List
import core.config.constants as constants
from core.exceptions.game_exceptions import MovementError, LogicError
from core.io_layers.board_printer import BoardPrinter

class InteractionController:
    """
    Acts as the central input handler, translating raw user commands into
    specific actions within the game's movement and state systems.
    """
    def __init__(self, movement_controller, board_state, game_status, manager):
        self.movement = movement_controller
        self.board = board_state
        self.status = game_status
        self.manager = manager

        self._dispatch_map = {
            "click": self._handle_click,
            "jump": self._handle_jump,
            "wait": self._handle_wait,
            "print": self._handle_print
        }

    def execute_command(self, action: str, args: list):
        handler = self._dispatch_map.get(action.lower())
        if handler:
            try:
                handler(args)
            except (MovementError, LogicError):
                self.status.selected_pos = None

    def _handle_click(self, args):
        row, col = int(args[0]), int(args[1])

        if not (0 <= row < self.board.height and 0 <= col < self.board.width):
            return

        if self.status.selected_pos is None:
            if self.board.get_token(row, col) != constants.EMPTY_CELL:
                self.status.selected_pos = (row, col)
        else:
            self.movement.execute_move(self.status.selected_pos, (row, col))
            self.status.selected_pos = None

    def _handle_jump(self, args: List[str]):
        try:
            row, col = self.mapper.pixel_to_grid(int(args[0]), int(args[1]))
            self.movement.prepare_airborne_move(row, col)
        except (ValueError, IndexError):
            raise LogicError("Invalid jump coordinate arguments.")

    def _handle_wait(self, args: List[str]):
        try:
            self.manager.process_time_tick(int(args[0]))
        except (ValueError, IndexError):
            raise LogicError("Invalid time tick argument.")

    def _handle_print(self, args: List[str]):
        BoardPrinter.print_board(self.board.matrix)