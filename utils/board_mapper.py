# utils/board_mapper.py
from typing import Tuple
import core.config.constants as constants

class BoardMapper:
    """
    Handles the conversion between matrix grid coordinates and screen pixel coordinates
    to facilitate rendering and interaction logic within the application.
    """
    def __init__(self, cell_size: int = constants.CELL_SIZE):
        """
        Initializes the coordinate translator with a specific pixel cell dimension.
        """
        self._cell_size = cell_size

    def pixel_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """
        Translates raw screen pixel coordinates (x, y) into matrix grid indices (row, col).
        """
        col = round((x - self._cell_size / 2) / self._cell_size)
        row = round((y - self._cell_size / 2) / self._cell_size)
        return row, col

    def grid_to_pixel_center(self, row: int, col: int) -> Tuple[int, int]:
        """
        Converts matrix grid indices (row, col) back into screen pixel coordinates (x, y)
        pointing directly to the center of that specific cell.
        """
        x = (col * self._cell_size) + (self._cell_size // 2)
        y = (row * self._cell_size) + (self._cell_size // 2)
        return x, y