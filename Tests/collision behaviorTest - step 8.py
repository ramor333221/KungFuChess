import unittest
from ChessGame import ChessGame


class TestAdvancedRealTimeInteractions(unittest.TestCase):

    def test_enemy_collision_only_at_landing(self):
        """1. בדיקה שכלי אויב ביעד נשאר גלוי בלוח עד לרגע הנחיתה המדויק"""
        grid = [
            ["wR", ".", "bR"],
            [".",  ".", "."]
        ]
        game = ChessGame(grid)

        # צריח לבן תוקף צריח שחור ב-(0, 2)
        game.click(50, 50)
        game.click(250, 50)

        # מחכים 500ms - הצריח הלבן בדרך, השחור עדיין חייב להיות ביעד!
        game.wait(500)
        self.assertEqual(game.grid[0][2], "bR", "Enemy piece should still be visible during flight")
        self.assertEqual(game.grid[0][0], ".", "Source piece should be cleared immediately")

        # מחכים עוד 500ms (סך הכל 1000ms) - כעת מתבצעת האכילה
        game.wait(500)
        self.assertEqual(game.grid[0][2], "wR", "Enemy piece should be captured after full arrival time")

    def test_invalid_premove_due_to_blocked_path(self):
        """2. מהלך מוקדם לא חוקי: ניסיון להניע כלי כשהמסלול חסום כרגע"""
        grid = [
            ["wR", "bP", "."],
            [".",  ".",  "."]
        ]
        game = ChessGame(grid)

        # ניסיון להניע את הצריח מעבר לחייל החוסם, מ-(0,0) ל-(0,2)
        game.click(50, 50)
        game.click(250, 50)

        # בגלל שהמסלול חסום ברגע הלחיצה, המהלך צריך להיפסל מיד
        self.assertEqual(len(game.pending_movements), 0, "Move should be rejected if path is blocked")
        self.assertEqual(game.grid[0][0], "wR", "Piece should not leave its source if move is illegal")

    def test_friendly_piece_landing_rejected(self):
        """3. נחיתה על כלי חבר: ניסיון לנוע למשבצת שבה נמצא כלי מאותו צבע"""
        grid = [
            ["wR", ".", "wP"],
            [".",  ".", "."]
        ]
        game = ChessGame(grid)

        # ניסיון להניע צריח לבן מ-(0,0) אל פיון לבן ב-(0,2)
        game.click(50, 50)
        game.click(250, 50)

        self.assertEqual(len(game.pending_movements), 0, "Move should be rejected when targeting a friendly piece")
        self.assertEqual(game.grid[0][0], "wR", "Piece must stay at source")

    def test_global_movement_conflict_lock(self):
        """4. קונפליקט תנועה גלובלי: כלי בטיסה נועל את המערכת מלקבל תנועות חדשות"""
        grid = [
            ["wR", ".", "."],
            ["wP", ".", "."],
            [".",  ".", "."]
        ]
        game = ChessGame(grid)

        # תנועה ראשונה: צריח זז מ-(0,0) ל-(0,2)
        game.click(50, 50)
        game.click(250, 50)
        self.assertEqual(len(game.pending_movements), 1, "First move should be accepted")

        # מחכים 500ms - הצריח עדיין באוויר
        game.wait(500)

        # ניסיון להניע כלי אחר (הפיון ב-1,0) בזמן שהצריח טס
        game.click(50, 150)
        game.click(50, 250)

        # המערכת בנעילה גלובלית, המהלך של הפיון חייב להיזרק!
        self.assertEqual(len(game.pending_movements), 1, "Global lock should reject secondary movements during flight")
        self.assertEqual(game.grid[1][0], "wP", "The second piece should not have moved or disappeared")


if __name__ == "__main__":
    unittest.main()