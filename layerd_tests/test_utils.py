# tests/test_utils.py
import unittest
from utils.board_mapper import BoardMapper

class TestBoardMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = BoardMapper(cell_size=100)

    def test_pixel_to_grid(self):
        row, col = self.mapper.pixel_to_grid(150, 250)
        self.assertEqual(row, 2)
        self.assertEqual(col, 1)

    def test_grid_to_pixel_center(self):
        x, y = self.mapper.grid_to_pixel_center(2, 1)
        self.assertEqual(x, 150)
        self.assertEqual(y, 250)

if __name__ == "__main__":
    unittest.main()