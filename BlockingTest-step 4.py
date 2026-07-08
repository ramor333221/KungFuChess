import unittest
from io import StringIO
import contextlib
import sys

from BoardRepresentation import BoardRepresentation
import main
from ChessGame import ChessGame


class TestChessGameStep2(unittest.TestCase):

    # --- בדיקות דפוסי תנועה בסיסיים ---

    def test_king_movement(self):
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wK', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        game.click(150, 150)
        game.click(50, 50)
        self.assertEqual(board.get_token(0, 0), 'wK')

        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 0), 'wK')

    def test_rook_movement(self):
        board = BoardRepresentation([['wR', '.', '.'], ['.', '.', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        game.click(50, 50)
        game.click(150, 150)
        self.assertEqual(board.get_token(0, 0), 'wR')

        game.click(50, 50)
        game.click(50, 250)
        self.assertEqual(board.get_token(2, 0), 'wR')

    def test_bishop_movement(self):
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wB', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        game.click(150, 150)
        game.click(150, 50)
        self.assertEqual(board.get_token(1, 1), 'wB')

        game.click(150, 150)
        game.click(250, 250)
        self.assertEqual(board.get_token(2, 2), 'wB')

    def test_queen_movement(self):
        board = BoardRepresentation([['wQ', '.', '.'], ['.', '.', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 2), 'wQ')

    def test_knight_movement(self):
        board = BoardRepresentation([
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', 'wN', '.', '.'],
            ['.', '.', '.', '.']
        ])
        game = ChessGame(board)
        game.click(150, 250)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 2), 'wN')

    # --- בדיקות לוגיקת בחירה והחלפת כלים ---

    def test_chess_game_switch_selection(self):
        board = BoardRepresentation([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['wK', '.', '.']
        ])
        game = ChessGame(board)

        game.click(50, 50)
        self.assertEqual(game._selected_pos, (0, 0))

        # לחיצה על כלי מאותו הצבע משנה בחירה אליו
        game.click(50, 250)
        self.assertEqual(game._selected_pos, (2, 0))

        # תוקן סופית: הציפייה הנכונה למשבצת (1,0) היא נקודה (ריקה) כי לא בוצעה תנועה!
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