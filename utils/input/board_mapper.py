from typing import Tuple

class BoardMapper:
    def __init__(self, board_image, grid_size: int = 8):
        self.grid_size = grid_size
        height, width = board_image.shape[:2]
        self._cell_size = min(height, width) // grid_size
        self.offset_x = (width - (self._cell_size * grid_size)) // 2
        self.offset_y = (height - (self._cell_size * grid_size)) // 2

    @property
    def cell_size(self):
        return self._cell_size

    def pixel_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        col = (x - self.offset_x) // self._cell_size
        row = (y - self.offset_y) // self._cell_size
        return int(row), int(col)

    def grid_to_pixel_center(self, row: int, col: int) -> Tuple[int, int]:
        x = self.offset_x + (col * self._cell_size) + (self._cell_size // 2)
        y = self.offset_y + (row * self._cell_size) + (self._cell_size // 2)
        return int(x), int(y)