from typing import List

EMPTY_CELL = '.'

class BoardRepresentation:
    def __init__(self, matrix: List[List[str]]):
        self._matrix = matrix
        self._height = len(matrix)
        self._width = len(matrix[0]) if self._height > 0 else 0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self._height and 0 <= col < self._width

    def get_token(self, row: int, col: int) -> str:
        return self._matrix[row][col]

    def is_empty(self, row: int, col: int) -> bool:
        return self._matrix[row][col] == EMPTY_CELL

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        self._matrix[to_row][to_col] = self._matrix[from_row][from_col]
        self._matrix[from_row][from_col] = EMPTY_CELL

    def to_canonical_string(self) -> str:
        return "\n".join(" ".join(row) for row in self._matrix)