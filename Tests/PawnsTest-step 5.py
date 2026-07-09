import unittest
from ChessGame import ChessGame


class TestPawnMovementRules(unittest.TestCase):

    def test_white_pawn_moves_upward_single_step(self):
        # לוח עם רגלי לבן בשורה 2
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # לחיצה על הרגלי (משבצת 2,1 -> x=150, y=250)
        game.click(150, 250)
        # לחיצה צעד אחד למעלה (משבצת 1,1 -> x=150, y=150)
        game.click(150, 150)

        self.assertEqual(game.grid[1][1], "wP")
        self.assertEqual(game.grid[2][1], ".")

    def test_black_pawn_moves_downward_single_step(self):
        # לוח עם רגלי שחור בשורה 1
        grid = [
            [".", ".", "."],
            [".", "bP", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # לחיצה על הרגלי (משבצת 1,1 -> x=150, y=150)
        game.click(150, 150)
        # לחיצה צעד אחד למטה (משבצת 2,1 -> x=150, y=250)
        game.click(150, 250)

        self.assertEqual(game.grid[2][1], "bP")
        self.assertEqual(game.grid[1][1], ".")

    def test_pawn_cannot_move_two_cells(self):
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # ניסיון להזיז 2 צעדים למעלה (משורה 2 לשורה 0)
        game.click(150, 250)
        game.click(150, 50)

        # הרגלי לא אמור לזוז
        self.assertEqual(game.grid[2][1], "wP")
        self.assertEqual(game.grid[0][1], ".")

    def test_pawn_cannot_capture_forward(self):
        # כלי שחור חוסם את הרגלי הלבן ישירות מלפניו
        grid = [
            [".", ".", "."],
            [".", "bK", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # ניסיון ללחוץ על הרגלי ואז על המלך שחוסם אותו קדימה
        game.click(150, 250)
        game.click(150, 150)

        # התנועה אסורה, המצב נשאר ללא שינוי
        self.assertEqual(game.grid[2][1], "wP")
        self.assertEqual(game.grid[1][1], "bK")

    def test_pawn_captures_diagonally(self):
        # מלך שחור נמצא באלכסון של הרגלי הלבן
        grid = [
            [".", ".", "."],
            ["bK", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # לחיצה על הרגלי הלבן (2,1 -> x=150, y=250)
        game.click(150, 250)
        # לחיצה על המלך השחור באלכסון (1,0 -> x=50, y=150)
        game.click(50, 150)

        # האכילה חוקית והרגלי תופס את מקום המלך
        self.assertEqual(game.grid[1][0], "wP")
        self.assertEqual(game.grid[2][1], ".")

    def test_pawn_cannot_move_diagonally_without_capture(self):
        # משבצת האלכסון ריקה
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # ניסיון לזוז באלכסון למשבצת ריקה (1,0)
        game.click(150, 250)
        game.click(50, 150)

        # התנועה צריכה להיכשל כי אין שם כלי לאכול
        self.assertEqual(game.grid[2][1], "wP")
        self.assertEqual(game.grid[1][0], ".")


if __name__ == "__main__":
    unittest.main()