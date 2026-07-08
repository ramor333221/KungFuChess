from typing import List, Set, Optional

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

    def get_row(self, row_idx: int) -> List[str]:
        return self._matrix[row_idx]

    def to_canonical_string(self) -> str:
        return "\n".join(" ".join(row) for row in self._matrix)