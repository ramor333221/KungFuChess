import unittest
from io import StringIO
import contextlib
import sys

from BoardRepresentation import BoardRepresentation
from ChessGame import ChessGame
from BoardParser import BoardParser
from BoardValidator import BoardValidator
import main


class TestChessProjectStep2(unittest.TestCase):

    # ==========================================
    # 1. בדיקות עבור BoardRepresentation
    # ==========================================
    def test_board_representation_basic(self):
        matrix = [['wR', '.'], ['.', 'bK']]
        board = BoardRepresentation(matrix)

        self.assertEqual(board.width, 2)
        self.assertEqual(board.height, 2)
        self.assertTrue(board.is_within_bounds(0, 0))
        self.assertFalse(board.is_within_bounds(2, 2))
        self.assertEqual(board.get_token(0, 0), 'wR')
        self.assertTrue(board.is_empty(0, 1))
        self.assertFalse(board.is_empty(0, 0))

    def test_board_representation_empty(self):
        board = BoardRepresentation([])
        self.assertEqual(board.width, 0)
        self.assertEqual(board.height, 0)

    def test_board_representation_move(self):
        matrix = [['wR', '.'], ['.', 'bK']]
        board = BoardRepresentation(matrix)

        board.move_piece(0, 0, 0, 1)  # מזיז את wR ימינה לתא הריק
        self.assertTrue(board.is_empty(0, 0))
        self.assertEqual(board.get_token(0, 1), 'wR')

    # ==========================================
    # 2. בדיקות עבור ChessGame (לוגיקת הקליקים והזמן)
    # ==========================================
    def test_chess_game_click_flow(self):

        matrix = [
            ['wP', '.'],
            ['.', 'bP']
        ]
        board = BoardRepresentation(matrix)
        game = ChessGame(board)

        # קליק מחוץ לגבולות הלוח (למשל x=250, y=50) - אמור להתעלם
        game.click(250, 50)

        # קליק על תא ריק כששום דבר לא נבחר (x=150, y=50 -> שורה 0, עמודה 1) - אמור להתעלם
        game.click(150, 50)

        # קליק על כלי לבן (x=50, y=50 -> שורה 0, עמודה 0) - בוחר את הכלי
        game.click(50, 50)

        # קליק על תא ריק (x=150, y=50 -> שורה 0, עמודה 1) - מבצע תנועה ומאפס בחירה
        game.click(150, 50)
        self.assertTrue(board.is_empty(0, 0))
        self.assertEqual(board.get_token(0, 1), 'wP')

    def test_chess_game_switch_selection(self):
        # בדיקה שקליק על כלי אחר מאותו הצבע מחליף את הבחירה
        matrix = [
            ['wP', 'wR'],
            ['.', '.']
        ]
        board = BoardRepresentation(matrix)
        game = ChessGame(board)

        game.click(50, 50)  # בוחר את wP (0, 0)
        game.click(150, 50)  # בוחר את wR (0, 1) במקום, כי שניהם לבנים ('w')
        game.click(50, 150)  # מזיז את wR לתא הריק (1, 0)

        self.assertEqual(board.get_token(1, 0), 'wR')
        self.assertEqual(board.get_token(0, 0), 'wP')  # wP נשאר במקומו

    def test_chess_game_wait_and_print(self):
        board = BoardRepresentation([['wK']])
        game = ChessGame(board)

        game.wait(500)
        self.assertEqual(game._game_clock_ms, 500)

        f = StringIO()
        with contextlib.redirect_stdout(f):
            game.print_board()
        self.assertEqual(f.getvalue().strip(), "wK")

    # ==========================================
    # 3. בדיקות עבור BoardParser
    # ==========================================
    def test_parser_valid_stream(self):
        input_data = (
            "Board:\n"
            "wR .\n"
            ". bK\n"
            "Commands:\n"
            "click 50 50\n"
            "wait 100\n"
            "print board\n"
        )
        parser = BoardParser(StringIO(input_data))
        raw_rows, command_lines = parser.parse_input()

        self.assertEqual(raw_rows, [['wR', '.'], ['.', 'bK']])
        self.assertEqual(command_lines, ['click 50 50', 'wait 100', 'print board'])

    # ==========================================
    # 4. בדיקות עבור BoardValidator
    # ==========================================
    def test_validator_errors(self):
        validator = BoardValidator()

        # שגיאת אורך שורות לא תואם
        f = StringIO()
        with contextlib.redirect_stdout(f):
            res = validator.validate([['wK'], ['.', '.']])
        self.assertIsNone(res)
        self.assertIn("ERROR ROW_WIDTH_MISMATCH", f.getvalue())

        # שגיאת טוקן לא מוכר
        f = StringIO()
        with contextlib.redirect_stdout(f):
            res = validator.validate([['wK', 'zP']])  # 'z' צבע לא חוקי
        self.assertIsNone(res)
        self.assertIn("ERROR UNKNOWN_TOKEN", f.getvalue())

    # ==========================================
    # 5. בדיקות מקצה לקצה לפונקציית ה-main
    # ==========================================
    def test_main_execution_flow(self):
        input_data = (
            "Board:\n"
            "wP .\n"
            ". bK\n"
            "Commands:\n"
            "click 50 50\n"
            "click 150 50\n"
            "print board\n"
        )
        fake_input = StringIO(input_data)
        fake_output = StringIO()

        # הזרקת הסטרימים בצורה בטוחה לטובת ה-main
        original_stdin = sys.stdin
        sys.stdin = fake_input

        try:
            with contextlib.redirect_stdout(fake_output):
                main.main()
        finally:
            sys.stdin = original_stdin

        # צפי: ה-wP יזוז משבצת אחת ימינה ואז הלוח יודפס
        expected_output = ". wP\n. bK"
        self.assertEqual(fake_output.getvalue().strip(), expected_output)

    def test_main_execution_invalid_arguments_ignored(self):
        # וידוא שפקודות עם ארגומנטים לא תקינים/לא מספרים פשוט נסלחות ולא קורסות
        input_data = (
            "Board:\n"
            "wK\n"
            "Commands:\n"
            "click abc 50\n"
            "wait xyz\n"
            "print board\n"
        )
        fake_input = StringIO(input_data)
        fake_output = StringIO()

        original_stdin = sys.stdin
        sys.stdin = fake_input
        try:
            with contextlib.redirect_stdout(fake_output):
                main.main()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(fake_output.getvalue().strip(), "wK")


if __name__ == '__main__':
    unittest.main()