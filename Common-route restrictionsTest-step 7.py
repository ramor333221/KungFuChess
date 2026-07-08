import unittest
from ChessGame import ChessGame


class TestMovementInterruptionAndCooldown(unittest.TestCase):

    def test_cannot_redirect_piece_while_moving(self):
        # לוח התחלתי עם צריח לבן ב-(0,0)
        grid = [
            ["wR", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # פקודה ראשונה: תנועה מ-(0,0) ל-(0,2) [x=50,y=50 -> x=250,y=50]
        game.click(50, 50)
        game.click(250, 50)

        # מקדמים את השעון ב-500ms (הצריח עדיין בדרך)
        game.wait(500)

        # ניסיון לבצע תנועה חדשה או לשנות כיוון בזמן שהצריח נעול בטיסה
        game.click(50, 50)
        game.click(50, 250)

        # נרוץ עוד 500ms כדי להגיע ל-1000ms (זמן הנחיתה של התנועה הראשונה)
        game.wait(500)

        # מוודאים שהצריח נחת ביעד המקורי שלו (0,2) ולא הושפע מהניסיון לשנות כיוון
        self.assertEqual(game.grid[0][2], "wR")
        self.assertEqual(game.grid[0][0], ".")
        self.assertEqual(game.grid[2][0], ".")

    def test_immediate_move_after_arrival_no_cooldown(self):
        grid = [
            ["wR", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # תנועה ראשונה: מ-(0,0) ל-(0,2)
        game.click(50, 50)
        game.click(250, 50)

        # המתנה של 1000ms מלאים - הצריח משלים הגעה
        game.wait(1000)

        # הדפסת הלוח או הרצת הלוגיקה הפנימית כדי לוודא נחיתה
        game._implement_movement()

        # תנועה שנייה מיידית: מ-(0,2) ל-(2,2) [x=250,y=50 -> x=250,y=250] בלי שום Cooldown
        game.click(250, 50)
        game.click(250, 250)

        # נחכה עוד 1000ms עבור התנועה השנייה
        game.wait(1000)

        # מוודאים שהצריח הגיע בהצלחה ליעד השני
        self.assertEqual(game.grid[2][2], "wR")
        self.assertEqual(game.grid[0][2], ".")


if __name__ == "__main__":
    unittest.main()