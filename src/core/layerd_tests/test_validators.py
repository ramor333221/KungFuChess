import unittest
from src.core.validators.board_validator import BoardValidator
from src.core.exceptions.game_exceptions import BoardValidationError


class TestBoardValidator(unittest.TestCase):
    def setUp(self):
        self.validator = BoardValidator()

    def test_row_width_mismatch(self):
        # Arrange: Create a matrix with uneven rows
        raw_matrix = [["wK", "wQ"], ["wP"]]

        # Act & Assert: This test now passes because we EXPECT the error
        with self.assertRaises(BoardValidationError) as cm:
            self.validator.validate(raw_matrix)
        self.assertEqual(str(cm.exception), "ROW_WIDTH_MISMATCH")

    def test_unknown_token(self):
        # Arrange: Create a matrix with an invalid token 'XX'
        raw_matrix = [["wK", "XX"]]

        # Act & Assert: This test now passes because we EXPECT the error
        with self.assertRaises(BoardValidationError) as cm:
            self.validator.validate(raw_matrix)
        self.assertIn("UNKNOWN_TOKEN", str(cm.exception))