# tests/test_validators.py
import unittest
from validators.board_validator import BoardValidator
from models.board_state import BoardState

class TestBoardValidator(unittest.TestCase):
    def setUp(self):
        self.validator = BoardValidator()

    def test_valid_board(self):
        raw_matrix = [
            ["bR", "bN", "bB"],
            [".",  ".",  "."],
            ["wR", "wN", "wB"]
        ]
        board_state = self.validator.validate(raw_matrix)
        self.assertIsNotNone(board_state)
        self.assertIsInstance(board_state, BoardState)
        self.assertEqual(board_state.matrix, raw_matrix)

    def test_row_width_mismatch(self):
        raw_matrix = [
            ["bR", "bN"],
            [".",  ".", "."],
            ["wR", "wN"]
        ]
        board_state = self.validator.validate(raw_matrix)
        self.assertIsNone(board_state)  # Fixed here

    def test_unknown_token(self):
        raw_matrix = [
            ["bR", "XX"],
            [".",  "."]
        ]
        board_state = self.validator.validate(raw_matrix)
        self.assertIsNone(board_state)  # Fixed here

if __name__ == "__main__":
    unittest.main()