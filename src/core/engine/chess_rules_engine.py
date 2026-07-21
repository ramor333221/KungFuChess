from config import constants
from src.core.engine.Piece_rule import KingRule, KnightRule, SlidingRule, PawnRule
from src.core.exceptions.game_exceptions import MovementError, LogicError


class ChessRulesEngine:
    """
    Central engine responsible for validating move legality by delegating
    checks to specific piece rule implementations.
    """

    def __init__(self):
        self.rules = {
            "K": KingRule(),
            "N": KnightRule(),
            "R": SlidingRule(check_straight=True),
            "B": SlidingRule(check_diagonal=True),
            "Q": SlidingRule(check_diagonal=True, check_straight=True),
            "P": PawnRule()
        }

    def is_move_legal(self, matrix, moved_pieces, piece_token, from_pos, to_pos, is_airborne=False) -> bool:
        """
        Validates if a move is legal for a given piece.
        Raises MovementError if the move violates game rules.
        """
        self._validate_basic_move(matrix, piece_token, to_pos)

        piece_type = piece_token[1]
        rule = self.rules.get(piece_type)

        if not rule:
            raise LogicError(f"No rule defined for piece type: {piece_type}")

        if piece_type == "P":
            is_legal = rule.is_legal(matrix, from_pos, to_pos, is_airborne,
                                     color=piece_token[0], moved_pieces=moved_pieces)
        else:
            is_legal = rule.is_legal(matrix, from_pos, to_pos, is_airborne)

        if not is_legal:
            raise MovementError(f"Illegal {piece_type} move from {from_pos} to {to_pos}.")

        return True

    def _validate_basic_move(self, matrix, piece_token, to_pos) -> None:
        """
        Performs preliminary checks: target within bounds and target not occupied
        by a piece of the same color. Raises MovementError on failure.
        """
        height, width = len(matrix), len(matrix[0])

        if not (0 <= to_pos[0] < height and 0 <= to_pos[1] < width):
            raise MovementError("Target position is out of board bounds.")

        target = matrix[to_pos[0]][to_pos[1]]

        if target is not None and target != constants.EMPTY_CELL:
            if target[0] == piece_token[0]:
                raise MovementError("Cannot capture your own piece.")