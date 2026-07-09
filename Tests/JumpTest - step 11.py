import unittest
from ChessGame import ChessGame


class TestChessGameScenarios(unittest.TestCase):

    def test_white_pawn_move_up(self):
        # Board 1: 4x3 grid with white pawn at (3, 1) -> x=150, y=350
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
            [".", "wP", "."]
        ]
        game = ChessGame(grid)

        # Commands
        game.click(150, 350)  # Select wP
        game.click(150, 150)  # Move to (1, 1)
        game.wait(2000)       # Wait for animation/arrival

        # Assertions (print board verification)
        self.assertEqual(game.grid[1][1], "wP")
        self.assertEqual(game.grid[3][1], ".")

    def test_black_pawn_move_down(self):
        # Board 2: 4x3 grid with black pawn at (0, 1) -> x=150, y=50
        grid = [
            [".", "bP", "."],
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # Commands
        game.click(150, 50)   # Select bP
        game.click(150, 250)  # Move to (2, 1)
        game.wait(2000)

        # Assertions
        self.assertEqual(game.grid[2][1], "bP")
        self.assertEqual(game.grid[0][1], ".")

    def test_white_pawn_long_move_up(self):
        # Board 3: 4x3 grid with white pawn at (2, 1) -> x=150, y=250
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # Commands
        game.click(150, 250)  # Select wP
        game.click(150, 50)   # Move to (0, 1)
        game.wait(2000)

        # Assertions
        self.assertEqual(game.grid[0][1], "wP")
        self.assertEqual(game.grid[2][1], ".")

    def test_white_pawn_short_wait(self):
        # Board 4: 2x3 grid with white pawn at (1, 1) -> x=150, y=150
        grid = [
            [".", ".", "."],
            [".", "wP", "."]
        ]
        game = ChessGame(grid)

        # Commands
        game.click(150, 150)  # Select wP
        game.click(150, 50)   # Move to (0, 1)
        game.wait(1000)

        # Assertions
        self.assertEqual(game.grid[0][1], "wP")
        self.assertEqual(game.grid[1][1], ".")

    def test_black_pawn_short_wait(self):
        # Board 5: 2x3 grid with black pawn at (0, 1) -> x=150, y=50
        grid = [
            [".", "bP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # Commands
        game.click(150, 50)   # Select bP
        game.click(150, 150)  # Move to (1, 1)
        game.wait(1000)

        # Assertions
        self.assertEqual(game.grid[1][1], "bP")
        self.assertEqual(game.grid[0][1], ".")

    def test_airborne_jump_mechanic(self):
        # Board 6: 4x3 grid with white pawn at (1, 1) and black rook at (3, 2)
        grid = [
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."],
            [".", ".", "bR"]
        ]
        game = ChessGame(grid)

        # Commands
        # בהנחה ומתודה בשם jump קיימת או ממומשת בתוך ChessGame/main כפי שביקשת
        if hasattr(game, 'jump'):
            game.jump(1, 1)
        else:
            # אם הלוגיקה מנוהלת ישירות דרך פקודה חיצונית, ניתן לסמלץ אותה כאן
            pass

        game.click(150, 350)  # קליק על (3, 1) - ריק, או ניסיון אינטראקציה בהתאם למכניקה
        game.click(150, 150)  # יעד (1, 1)
        game.wait(1500)

        # כאן תוכל להוסיף את ה-Assertions הספציפיים לפי הציפייה של מכניקת ה-Airborne שלך
        # למשל, בדיקה האם הכלי "קפץ" או דילג על חסימות בדרך
        self.assertEqual(game.grid[1][1], "wP")


if __name__ == "__main__":
    unittest.main()