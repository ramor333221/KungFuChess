from core.models.board_state import BoardState
from core.models.game_status import GameStatus


class MovementValidator:
    def __init__(self, board_state: BoardState, game_status: GameStatus):
        self._board = board_state
        self._status = game_status

    def can_interact_with_cell(self, row: int, col: int) -> bool:
        """Verifies if a coordinate interaction is allowed under current system conditions."""
        if self._status.game_over:
            return False

        if not self._board.is_within_bounds(row, col):
            return False

        return True