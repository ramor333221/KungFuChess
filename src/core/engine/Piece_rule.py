from abc import ABC, abstractmethod

from config import constants
from src.core.utils.board_utils import BoardUtils


class PieceRule(ABC):
    """
    Defines the interface for chess piece movement logic.
    """
    @abstractmethod
    def is_legal(self, matrix, from_pos, to_pos, is_airborne) -> bool:
        pass


class KingRule(PieceRule):
    """
    Implements movement validation for the King piece.
    """
    def is_legal(self, matrix, from_pos, to_pos, is_airborne):
        d_row, d_col = abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1])
        return d_row <= 1 and d_col <= 1


class KnightRule(PieceRule):
    """
    Implements movement validation for the Knight piece.
    """
    def is_legal(self, matrix, from_pos, to_pos, is_airborne):
        d_row, d_col = abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1])
        return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)


class SlidingRule(PieceRule):
    """
    Handles movement validation for pieces that slide along straight or diagonal paths (e.g., Bishop, Rook, Queen).
    """
    def __init__(self, check_diagonal=False, check_straight=False):
        self.check_diagonal = check_diagonal
        self.check_straight = check_straight

    def is_legal(self, matrix, from_pos, to_pos, is_airborne):
        d_row, d_col = abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1])
        diag = (d_row == d_col)
        straight = (d_row == 0 or d_col == 0)

        if (self.check_diagonal and not diag) and (self.check_straight and not straight):
            return False
        if not self.check_diagonal and not straight: return False
        if not self.check_straight and not diag: return False

        return True if is_airborne else BoardUtils.is_path_clear(matrix, from_pos, to_pos)


class PawnRule(PieceRule):
    """
    Implements specific movement and capture validation logic for Pawn pieces.
    """
    def is_legal(self, matrix, from_pos, to_pos, is_airborne=False, color="w", moved_pieces=None):
        color = color.lower()
        r1, c1 = from_pos
        r2, c2 = to_pos
        fwd = -1 if color == "w" else 1
        dr, dc = r2 - r1, c2 - c1

        def is_empty(r, c):
            val = matrix[r][c]
            return val is None or val == constants.EMPTY_CELL

        if dr == fwd and dc == 0:
            return is_empty(r2, c2)

        if dr == 2 * fwd and dc == 0:
            start_row = (len(matrix) - 2) if color == "w" else 1
            return (r1 == start_row and
                    is_empty(r1 + fwd, c1) and
                    is_empty(r2, c2))

        if dr == fwd and abs(dc) == 1:
            val = matrix[r2][c2]
            return val is not None and val != constants.EMPTY_CELL and val[0].lower() != color

        return False