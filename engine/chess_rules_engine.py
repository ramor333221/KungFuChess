# engine/chess_rules_engine.py
from typing import List, Tuple, Set
import config.constants as constants


class ChessRulesEngine:

    @staticmethod
    def is_path_clear(matrix: List[List[str]], from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        r1, c1 = from_pos
        r2, c2 = to_pos

        dr = (r2 - r1) // max(1, abs(r2 - r1)) if r1 != r2 else 0
        dc = (c2 - c1) // max(1, abs(c2 - c1)) if c1 != c2 else 0

        current_r = r1 + dr
        current_c = c1 + dc

        while (current_r, current_c) != to_pos:
            if matrix[current_r][current_c] != constants.EMPTY_CELL:
                return False
            current_r += dr
            current_c += dc

        return True

    def is_move_legal(self, matrix: List[List[str]], moved_pieces: Set[Tuple[int, int]],
                      piece_token: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        height = len(matrix)
        width = len(matrix[0]) if height > 0 else 0
        if not (0 <= to_pos[0] < height and 0 <= to_pos[1] < width):
            return False

        color = piece_token[0]
        piece_type = piece_token[1]

        target_token = matrix[to_pos[0]][to_pos[1]]
        if target_token != constants.EMPTY_CELL and target_token[0] == color:
            return False

        r1, c1 = from_pos
        r2, c2 = to_pos
        d_row, d_col = abs(r2 - r1), abs(c2 - c1)

        if d_row == 0 and d_col == 0:
            return False

        if piece_type == "K":
            return d_row <= 1 and d_col <= 1

        elif piece_type == "R":
            if d_row == 0 or d_col == 0:
                return self.is_path_clear(matrix, from_pos, to_pos)
            return False

        elif piece_type == "B":
            if d_row == d_col:
                return self.is_path_clear(matrix, from_pos, to_pos)
            return False

        elif piece_type == "Q":
            if d_row == 0 or d_col == 0 or d_row == d_col:
                return self.is_path_clear(matrix, from_pos, to_pos)
            return False

        elif piece_type == "N":
            return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)

        elif piece_type == "P":
            return self._is_pawn_move_legal(matrix, moved_pieces, color, from_pos, to_pos)

        return False

    def _is_pawn_move_legal(self, matrix: List[List[str]], moved_pieces: Set[Tuple[int, int]],
                            color: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        r1, c1 = from_pos
        r2, c2 = to_pos
        height = len(matrix)
        fwd = -1 if color == "w" else 1
        dr, dc = r2 - r1, c2 - c1

        # צעד אחד קדימה
        if dr == fwd and dc == 0:
            return matrix[r2][c2] == constants.EMPTY_CELL

        # צעד כפול קדימה משורת הבסיס האבסולוטית של הלוח
        if dr == 2 * fwd and dc == 0:
            starting_row = (height - 1) if color == "w" else 0
            if r1 == starting_row:
                return (matrix[r1 + fwd][c1] == constants.EMPTY_CELL and
                        matrix[r2][c2] == constants.EMPTY_CELL)

        # הכאה באלכסון
        if dr == fwd and abs(dc) == 1:
            return matrix[r2][c2] != constants.EMPTY_CELL and matrix[r2][c2][0] != color

        return False