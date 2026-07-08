import unittest
from io import StringIO
import contextlib

from Board.BoardRepresentation import BoardRepresentation
from BoardParser import BoardParser
from BoardValidator import BoardValidator
import main


class TestChessBoardParser(unittest.TestCase):

    # --- בדיקות עבור BoardRepresentation ---
    def test_board_representation_properties(self):
        matrix = [['wR', '.'], ['.', 'bK']]
        board = BoardRepresentation(matrix)

        self.assertEqual(board.width, 2)
        self.assertEqual(board.height, 2)
        self.assertEqual(board.get_row(0), ['wR', '.'])
        self.assertEqual(board.to_canonical_string(), "wR .\n. bK")

    def test_board_representation_empty(self):
        board = BoardRepresentation([])
        self.assertEqual(board.width, 0)
        self.assertEqual(board.height, 0)

    # --- בדיקות עבור BoardParser ---
    def test_parser_valid_input(self):
        input_data = (
            "\n"
            "Board:\n"
            "wR . bK\n"
            ". bP .\n"
            "Commands:\n"
            "move a1 a2\n"
        )
        stream = StringIO(input_data)
        parser = BoardParser(stream)

        raw_rows = parser.parse_raw_rows()
        expected = [
            ['wR', '.', 'bK'],
            ['.', 'bP', '.']
        ]
        self.assertEqual(raw_rows, expected)

    def test_parser_no_board_header(self):
        input_data = "wR . bK\n"
        stream = StringIO(input_data)
        parser = BoardParser(stream)

        self.assertEqual(parser.parse_raw_rows(), [])

    # --- בדיקות עבור BoardValidator ---
    def test_validator_success(self):
        validator = BoardValidator()
        raw_rows = [['wR', '.'], ['.', 'bK']]

        board = validator.validate(raw_rows)
        self.assertIsNotNone(board)
        self.assertEqual(board.width, 2)

    def test_validator_empty_input(self):
        validator = BoardValidator()
        self.assertIsNone(validator.validate([]))
        self.assertIsNone(validator.validate([[]]))

    def test_validator_row_width_mismatch(self):
        validator = BoardValidator()
        raw_rows = [
            ['wR', '.'],
            ['.', 'bK', '.']
        ]

        f = StringIO()
        with contextlib.redirect_stdout(f):
            board = validator.validate(raw_rows)

        self.assertIsNone(board)
        self.assertIn("ERROR ROW_WIDTH_MISMATCH", f.getvalue())

    def test_validator_unknown_token_length(self):
        validator = BoardValidator()
        raw_rows = [['wR', 'wRR']]

        f = StringIO()
        with contextlib.redirect_stdout(f):
            board = validator.validate(raw_rows)

        self.assertIsNone(board)
        self.assertIn("ERROR UNKNOWN_TOKEN", f.getvalue())

    def test_validator_unknown_token_invalid_color_or_piece(self):
        validator = BoardValidator()

        # צבע לא חוקי (z)
        f = StringIO()
        with contextlib.redirect_stdout(f):
            self.assertIsNone(validator.validate([['zK']]))
        self.assertIn("ERROR UNKNOWN_TOKEN", f.getvalue())

        # כלי לא חוקי (X)
        f = StringIO()
        with contextlib.redirect_stdout(f):
            self.assertIsNone(validator.validate([['wX']]))
        self.assertIn("ERROR UNKNOWN_TOKEN", f.getvalue())

    def test_validator_custom_rules(self):
        # בדיקה שהמערכת תומכת בחוקים מותאמים אישית (הזרקה של הבוס)
        custom_validator = BoardValidator(valid_colors={'g'}, valid_pieces={'X'})

        # 'gX' תקין לפי החוקים החדשים, 'wK' כבר לא חוקי
        self.assertIsNotNone(custom_validator.validate([['gX']]))

        f = StringIO()
        with contextlib.redirect_stdout(f):
            self.assertIsNone(custom_validator.validate([['wK']]))
        self.assertIn("ERROR UNKNOWN_TOKEN", f.getvalue())

    # --- בדיקות עבור פונקציית ה-main ---

    def test_main_flow_success(self):
        input_data = "Board:\nwR .\n. bK\nCommands:\n"

        fake_input = StringIO(input_data)
        fake_output = StringIO()

        with contextlib.redirect_stdout(fake_output):
            original_stdin = main.sys.stdin
            main.sys.stdin = fake_input
            try:
                main.main()
            finally:
                main.sys.stdin = original_stdin

        self.assertEqual(fake_output.getvalue().strip(), "wR .\n. bK")

    def test_main_flow_with_errors(self):
        input_data = "Board:\nwR .\n. bK .\nCommands:\n"
        fake_input = StringIO(input_data)
        fake_output = StringIO()

        with contextlib.redirect_stdout(fake_output):
            original_stdin = main.sys.stdin
            main.sys.stdin = fake_input
            try:
                main.main()
            finally:
                main.sys.stdin = original_stdin

        self.assertIn("ERROR ROW_WIDTH_MISMATCH", fake_output.getvalue())


if __name__ == '__main__':
    unittest.main()