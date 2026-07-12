# models/board_state.py
from typing import List
import config.constants as constants

class BoardState:
    def __init__(self, matrix: List[List[str]]):
        """
        Initializes the board representation with a 2D matrix of string tokens.
        """
        self._matrix = matrix
        self._height = len(matrix)
        self._width = len(matrix[0]) if self._height > 0 else 0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def matrix(self) -> List[List[str]]:
        """Exposes the raw grid configuration for the printer or external validators."""
        return self._matrix

    def is_within_bounds(self, row: int, col: int) -> bool:
        """Verifies if a specific row and column address exists inside the boundaries."""
        return 0 <= row < self._height and 0 <= col < self._width

    def get_token(self, row: int, col: int) -> str:
        """Retrieves the token code sitting at the targeted position (e.g., 'wP' or '.')."""
        return self._matrix[row][col]

    def set_token(self, row: int, col: int, token: str) -> None:
        """Explicitly replaces the cell element with a new token value."""
        self._matrix[row][col] = token

    def is_empty(self, row: int, col: int) -> bool:
        """Checks if a tile matches the configured EMPTY_CELL definition."""
        return self._matrix[row][col] == constants.EMPTY_CELL

    def clear_cell(self, row: int, col: int) -> None:
        """Resets a cell back to an empty placeholder."""
        self._matrix[row][col] = constants.EMPTY_CELL