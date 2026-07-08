import unittest
from ChessGame import ChessGame


class TestGameOverBehavior(unittest.TestCase):

    def test_king_capture_ends_game(self):
        """1. בדיקה שאכילת המלך האויב מעבירה את המשחק למצב Game Over רק ברגע הנחיתה"""
        grid = [
            ["wR", ".", "bK"],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # צריח לבן תוקף את המלך השחור שנמצא ב-(0, 2)
        game.click(50, 50)
        game.click(250, 50)

        # מחכים 500ms - הצריח בדרך, המלך עדיין חי והמשחק פעיל
        game.wait(500)
        self.assertFalse(game.game_over, "Game should not be over while the piece is still traveling")
        self.assertEqual(game.grid[0][2], "bK", "King should still be on the board during flight")

        # מחכים עוד 500ms (סך הכל 1000ms) - הצריח נוחת ומחסל את המלך
        game.wait(500)
        self.assertTrue(game.game_over, "Game should be officially over after King is captured")
        self.assertEqual(game.grid[0][2], "wR", "Rook should occupy the destination square")

    def test_commands_ignored_after_game_over(self):
        """2. בדיקה שלאחר סיום המשחק, פקודות תנועה חדשות נזרקות לחלוטין"""
        grid = [
            ["wR", ".", "bK"],
            ["wP", ".", "."]
        ]
        game = ChessGame(grid)

        # מהלך 1: צריח לבן מוריד את המלך השחור (לוקח 1000ms)
        game.click(50, 50)
        game.click(250, 50)
        game.wait(1000)

        # מוודאים שהמשחק אכן נגמר
        self.assertTrue(game.game_over)

        # ניסיון להניע כלי אחר (הפיון הלבן ב-1,0) לאחר ה-Game Over
        game.click(50, 150)
        game.click(50, 250)

        # המערכת צריכה להתעלם לחלוטין - הפיון לא צריך לזוז או להיעלם
        self.assertEqual(len(game.pending_movements), 0, "No new movements should be registered after game over")
        self.assertEqual(game.grid[1][0], "wP", "Friendly pieces should remain frozen where they were")


if __name__ == "__main__":
    unittest.main()