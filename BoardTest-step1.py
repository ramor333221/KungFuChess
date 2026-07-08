import unittest
from io import StringIO
import contextlib
import sys

from BoardRepresentation import BoardRepresentation
from ChessGame import ChessGame
import main


class TestChessGameStep2(unittest.TestCase):

    # --- בדיקות דפוסי תנועה בסיסיים ---

    def test_king_movement(self):
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wK', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה חוקית (אלכסון צעד אחד ל-0,0)
        game.click(150, 150)  # בחר מלך ב-(1,1)
        game.click(50, 50)  # זוז ל-(0,0)
        self.assertEqual(board.get_token(0, 0), 'wK')
        self.assertEqual(board.get_token(1, 1), '.')

        # תנועה לא חוקית (שני צעדים ימינה ל-0,2) -> נכשל ונשאר ב-0,0
        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 0), 'wK')

    def test_rook_movement(self):
        board = BoardRepresentation([['wR', '.', '.'], ['.', '.', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה לא חוקית (אלכסון) -> נשאר במקום
        game.click(50, 50)
        game.click(150, 150)
        self.assertEqual(board.get_token(0, 0), 'wR')

        # תנועה חוקית (קו ישר למטה ל-2,0)
        game.click(50, 50)
        game.click(50, 250)
        self.assertEqual(board.get_token(2, 0), 'wR')
        self.assertEqual(board.get_token(0, 0), '.')

    def test_bishop_movement(self):
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wB', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה לא חוקית (קו ישר למעלה) -> נשאר במקום
        game.click(150, 150)
        game.click(150, 50)
        self.assertEqual(board.get_token(1, 1), 'wB')

        # תנועה חוקית (אלכסון ל-2,2)
        game.click(150, 150)
        game.click(250, 250)
        self.assertEqual(board.get_token(2, 2), 'wB')
        self.assertEqual(board.get_token(1, 1), '.')

    def test_queen_movement(self):
        board = BoardRepresentation([['wQ', '.', '.'], ['.', '.', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה חוקית (קו ישר ימינה ל-0,2)
        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 2), 'wQ')

        # תנועה חוקית (אלכסון ל-2,0)
        game.click(250, 50)
        game.click(50, 250)
        self.assertEqual(board.get_token(2, 0), 'wQ')

        # תנועה לא חוקית (דמוי פרש) -> נשאר במקום
        game.click(50, 250)
        game.click(150, 50)
        self.assertEqual(board.get_token(2, 0), 'wQ')

    def test_knight_movement(self):
        board = BoardRepresentation([
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', 'wN', '.', '.'],
            ['.', '.', '.', '.']
        ])
        game = ChessGame(board)

        # תנועה חוקית בצורת L ל-(0,2)
        game.click(150, 250)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 2), 'wN')
        self.assertEqual(board.get_token(2, 1), '.')

    # --- בדיקות לוגיקת בחירה והחלפת כלים ---

    def test_chess_game_switch_selection(self):
        # לוח המכיל שני כלים לבנים
        board = BoardRepresentation([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['wK', '.', '.']
        ])
        game = ChessGame(board)

        # קליק ראשון על הצריח ב-(0,0)
        game.click(50, 50)
        self.assertEqual(game._selected_pos, (0, 0))

        # קליק שני על המלך ב-(2,0) -> מאותו הצבע, לכן הבחירה משתנה אליו!
        game.click(50, 250)
        self.assertEqual(game._selected_pos, (2, 0))

        # וידוא שהכלים לא זזו והמשבצת האמצעית נשארה ריקה (זה התיקון לשגיאה שלך)
        self.assertEqual(board.get_token(0, 0), 'wR')
        self.assertEqual(board.get_token(2, 0), 'wK')
        self.assertEqual(board.get_token(1, 0), '.')

    def test_click_same_square_keeps_selection(self):
        board = BoardRepresentation([['wK']])
        game = ChessGame(board)
        game.click(50, 50)
        game.click(50, 50)
        self.assertEqual(game._selected_pos, (0, 0))

        # --- בדיקת זרימת פקודות מקצה לקצה ---

    def test_main_with_valid_and_invalid_moves(self):
        input_data = (
            "Board:\n"
            "wK . .\n"
            ". . .\n"
            ". . .\n"
            "Commands:\n"
            "click 50 50\n"
            "click 250 50\n"
            "print board\n"
            "click 50 50\n"
            "click 150 150\n"
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

        expected = "wK . .\n. . .\n. . .\n. . .\n. wK .\n. . ."
        self.assertEqual(fake_output.getvalue().strip(), expected)


if __name__ == '__main__':
    unittest.main()