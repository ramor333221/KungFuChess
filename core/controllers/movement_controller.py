from typing import Tuple
import core.config.constants as constants
from core.exceptions.game_exceptions import MovementError, LogicError
# Assuming these are defined in models/interfaces.py
from core.models.interfaces import ReadOnlyBoard, MovementStatus

class MovementController:
    """
    Manages game piece movement, validating legality through the rules engine
    and coordinating between board state and movement animations or processing.
    """

    def __init__(self,
                 board_state: ReadOnlyBoard,
                 game_status: MovementStatus,
                 rules_engine,
                 status_manager):
        """
        board_state is now restricted to ReadOnlyBoard methods.
        game_status is now restricted to MovementStatus properties.
        """
        self.board = board_state
        self.status = game_status
        self.rules = rules_engine
        self.manager = status_manager
        self.is_airborne = False

    def set_airborne(self, state: bool):
        """
        Toggles the airborne state for upcoming move processing.
        """
        self.is_airborne = state

    def prepare_airborne_move(self, row: int, col: int):
        """
        Selects a piece and sets the system to airborne mode for a non-linear move.
        """
        token = self.board.get_token(row, col)
        if token == constants.EMPTY_CELL:
            raise LogicError("No piece selected to jump.")

        self.status.selected_pos = (row, col)
        self.is_airborne = True

    def execute_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        token = self.board.get_token(*from_pos)

        if self.rules.is_move_legal(
                self.board.matrix,
                self.status.moved_pieces,
                token,
                from_pos,
                to_pos,
                self.is_airborne
        ):
            if not hasattr(self.status, 'piece_states'):
                self.status.piece_states = {}

            self.status.piece_states[from_pos] = "move"

            if self.is_airborne:
                self.manager.add_airborne_movement(from_pos, to_pos, token)
            else:
                self.manager.add_linear_movement(from_pos, to_pos, token)

            self.status.piece_states[to_pos] = "long_rest"

            if from_pos in self.status.piece_states:
                del self.status.piece_states[from_pos]

            self.is_airborne = False
        else:
            raise MovementError(f"Illegal move from {from_pos} to {to_pos}.")
            
    def reset_selection(self):
        """
        Clears the current piece selection and resets airborne movement flags.
        """
        self.status.selected_pos = None
        self.is_airborne = False

    def get_legal_moves(self, row, col):
        legal_moves = []
        piece_token = self.board.matrix[row][col]

        for r in range(8):
            for c in range(8):
                try:
                    if self.rules.is_move_legal(self.board.matrix, [], piece_token, (row, col), (r, c)):
                        legal_moves.append((r, c))
                except Exception:
                    continue
        return legal_moves