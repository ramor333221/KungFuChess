import unittest
from io import StringIO
import contextlib
import sys

from BoardRepresentation import BoardRepresentation
from ChessGame import ChessGame
from BoardParser import BoardParser
from BoardValidator import BoardValidator
import main


class TestChessMovementAndLogic(unittest.TestCase):

    def test_king_movement(self):
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wK', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה חוקית (אלכסון צעד אחד ל-0,0)
        game.click(150, 150)  # בחר מלך
        game.click(50, 50)  # זוז
        self.assertEqual(board.get_token(0, 0), 'wK')

        # תנועה לא חוקית (שני צעדים ימינה ל-0,2) -> אמורה להיכשל ולהשאיר את המלך ב-0,0
        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(board.get_token(0, 0), 'wK')

    def test_rook_movement(self):
        board = BoardRepresentation([['wR', '.', '.'], ['.', '.', '.'], ['.', '.', '.'].copy()])
        game = ChessGame(board)

        # תנועה לא חוקית (אלכסון) -> נשאר במקום
        game.click(50, 50)
        game.click(150, 150)
        self.assertEqual(board.get_token(0, 0), 'wR')

        # תנועה חוקית (קו ישר למטה ל-2,0)
        game.click(50, 50)
        game.click(50, 250)
        self.assertEqual(board.get_token(2, 0), 'wR')

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
        board = BoardRepresentation([['.', '.', '.'], ['.', 'wN', '.'], ['.', '.', '.']])
        game = ChessGame(board)

        # תנועה לא חוקית (אלכסון צעד אחד) -> נשאר במקום
        game.click(150, 150)
        game.click(250, 250)
        self.assertEqual(board.get_token(1, 1), 'wN')

        # תנועה חוקית בצורת L
        wide_board = BoardRepresentation([
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', 'wN', '.', '.'],
            ['.', '.', '.', '.']
        ])
        wide_game = ChessGame(wide_board)
        wide_game.click(150, 250)
        wide_game.click(250, 50)
        self.assertEqual(wide_board.get_token(0, 2), 'wN')

    def test_pawn_always_legal_in_this_step(self):
        board = BoardRepresentation([['wP', '.'], ['.', '.']])
        game = ChessGame(board)
        game.click(50, 50)
        game.click(150, 150)
        self.assertEqual(board.get_token(1, 1), 'wP')

    def test_click_same_square_keeps_selection(self):
        board = BoardRepresentation([['wK']])
        game = ChessGame(board)
        game.click(50, 50)
        game.click(50, 50)
        self.assertEqual(game._selected_pos, (0, 0))

    def test_unknown_piece_type_fails_gracefully(self):
        board = BoardRepresentation([['wX', '.'], ['.', '.']])
        game = ChessGame(board)
        game.click(50, 50)
        game.click(150, 50)
        self.assertEqual(board.get_token(0, 0), 'wX')

    # --- בדיקות זרם פקודות מלא מקצה לקצה ---

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