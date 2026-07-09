import unittest
from ChessGame import ChessGame


class TestPawnAdvancedRules(unittest.TestCase):

    def test_pawn_double_step_from_start(self):
        """1. בדיקה שרגלי יכול לנוע 2 משבצות קדימה משורת ההתחלה שלו"""
        # לוח בגודל 8x3 כדי לדמות את שורת ההתחלה (שורה 1 עבור שחור, שורה 6 עבור לבן בלוגיקה הסטנדרטית)
        # כדי להתאים לגודל הלוח הדינמי, נשתמש בלוח בגובה 8 שורות
        grid = [
            [".", ".", "."],
            ["bP", ".", "."],  # שורה 1 - שורת התחלה של שחור
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "wP"],  # שורה 6 - שורת התחלה של לבן
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # מהלך 1: רגלי לבן (6, 2) זז ל-(4, 2) - צעד כפול
        game.click(250, 650)  # שורה 6, עמודה 2
        game.click(250, 450)  # שורה 4, עמודה 2
        self.assertEqual(len(game.pending_movements), 1, "White pawn should be allowed to double-step from row 6")
        game.wait(1000)
        self.assertEqual(game.grid[4][2], "wP")

        # מהלך 2: רגלי שחור (1, 0) זז ל-(3, 0) - צעד כפול
        game.click(50, 150)  # שורה 1, עמודה 0
        game.click(50, 350)  # שורה 3, עמודה 0
        self.assertEqual(len(game.pending_movements), 1, "Black pawn should be allowed to double-step from row 1")
        game.wait(1000)
        self.assertEqual(game.grid[3][0], "bP")

    def test_pawn_double_step_blocked(self):
        """2. בדיקה שצעד כפול נחסם אם יש כלי בדרך (במשבצת האמצע או היעד)"""
        grid = [
            [".", ".", "."],
            ["bP", "bP", "."],
            ["wR", ".", "."],  # חוסם את האמצע של החייל הראשון
            [".", "wR", "."],  # חוסם את היעד של החייל השני
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # ניסיון 1: חייל שחור מ-(1, 0) מנסה לזוז ל-(3, 0), אבל האמצע (2, 0) חסום
        game.click(50, 150)
        game.click(50, 350)
        self.assertEqual(len(game.pending_movements), 0, "Move should be rejected if the middle cell is blocked")

        # ניסיון 2: חייל שחור מ-(1, 1) מנסה לזוז ל-(3, 1), אבל היעד (3, 1) חסום
        game.click(150, 150)
        game.click(150, 350)
        self.assertEqual(len(game.pending_movements), 0, "Move should be rejected if the destination cell is blocked")

    def test_pawn_promotion_to_queen(self):
        """3. בדיקה שרגלי שהגיע לשורה האחרונה הופך אוטומטית למלכה (Q) ברגע הנחיתה"""
        grid = [
            [".", ".", "."],  # שורה 0 (שורת ההכתרה של לבן)
            ["wP", ".", "."],  # רגלי לבן מרחק צעד אחד מהסוף
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # הפיון הלבן זז מ-(1, 0) ל-(0, 0)
        game.click(50, 150)
        game.click(50, 50)

        # בזמן הטיסה (500ms) הוא עדיין לא הושפע בלוח האמיתי
        game.wait(500)
        self.assertEqual(game.grid[0][0], ".", "Destination should be empty during flight")

        # ברגע הנחיתה (סך הכל 1000ms) הוא חייב להפוך ל-wQ
        game.wait(500)
        self.assertEqual(game.grid[0][0], "wQ", "Pawn should be promoted to Queen upon reaching the last row")


if __name__ == "__main__":
    unittest.main()