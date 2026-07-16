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
            "print": self._handle_print,
            "switch_turn": self._handle_switch_turn
        }

    def execute_command(self, action: str, args: list):
        handler = self._dispatch_map.get(action.lower())
        if handler:
            try:
                handler(args)
            except (MovementError, LogicError):
                self.status.selected_pos = None

    def _handle_click(self, args):
        """
        Processes click input.
        Supports 2 arguments (row, col) for selection,
        or 4 arguments (r1, c1, r2, c2) for a full move command.
        """
        if len(args) == 4:
            src = (int(args[0]), int(args[1]))
            dst = (int(args[2]), int(args[3]))
            self.movement.execute_move(src, dst)
            self.status.selected_pos = None
            return

        if len(args) == 2:
            row, col = int(args[0]), int(args[1])

            if not (0 <= row < self.board.height and 0 <= col < self.board.width):
                print("DEBUG: Click out of bounds")
                return

            if self.status.selected_pos is None:
                token = self.board.get_token(row, col)
                if token != constants.EMPTY_CELL:
                    self.status.selected_pos = (row, col)
                else:
                    print("DEBUG: Clicked empty cell")
            else:
                self.movement.execute_move(self.status.selected_pos, (row, col))
                self.status.selected_pos = None

    def _is_same_color(self, pos1, pos2):
        token1 = self.board.get_token(pos1[0], pos1[1])
        token2 = self.board.get_token(pos2[0], pos2[1])
        return token1[0] == token2[0]

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

    def _handle_switch_turn(self, args: List[str]):
        """Toggles the current turn between 0 and 1."""
        self.status.current_turn = 1 - self.status.current_turn
        print(f"Turn switched to: {self.status.current_turn}")