# utils/board_mapper.py
from typing import Tuple
import config.constants as constants

class BoardMapper:
    def __init__(self, cell_size: int = constants.CELL_SIZE):
        """
        Initializes the coordinate translator with a specific pixel cell dimension.
        """
        self._cell_size = cell_size

    def pixel_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """
        Converts screen pixel coordinates (x, y) into matrix grid indices (row, col).
        Note: Screen X maps to grid columns, and Screen Y maps to grid rows.
        """
        col = x // self._cell_size
        row = y // self._cell_size
        return row, col

    def grid_to_pixel_center(self, row: int, col: int) -> Tuple[int, int]:
        """
        Converts matrix grid indices (row, col) back into screen pixel coordinates (x, y)
        pointing directly to the center of that specific cell.
        """
        x = (col * self._cell_size) + (self._cell_size // 2)
        y = (row * self._cell_size) + (self._cell_size // 2)
        return x, y