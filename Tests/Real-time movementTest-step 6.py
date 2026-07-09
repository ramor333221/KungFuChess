import unittest
from ChessGame import ChessGame


class TestMovementOverTime(unittest.TestCase):

    def test_piece_remains_in_original_position_before_arrival(self):
        # לוח התחלתי עם מלך לבן במשבצת (0,0)
        grid = [
            ["wK", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # לחיצה על המלך (0,0 -> x=50, y=50) ובחירת יעד חוקי (1,1 -> x=150, y=150)
        game.click(50, 50)
        game.click(150, 150)

        # אנחנו מקדמים את השעון ב-500 מילישניות בלבד (זמן ההגעה הוא +1000ms)
        game.wait(500)

        # וידוא שהכלי עדיין לא הגיע פיזית ללוח הפנימי (עבור פקודות/חסימות עתידיות)
        self.assertEqual(game.grid[1][1], ".")

        # וידוא שזמן הטיסה מציג את המלך במיקום המקורי שלו (0,0) בעזרת הדפסת הלוח או הלוגיקה הווירטואלית
        # נבדוק ישירות את ה-display_grid הווירטואלי דרך מנגנון הטיסה
        self.assertEqual(len(game.pending_movements), 1)
        self.assertEqual(game.pending_movements[0]["from"], (0, 0))
        self.assertEqual(game.pending_movements[0]["to"], (1, 1))

    def test_piece_appears_at_destination_after_enough_wait_time(self):
        grid = [
            ["wK", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        # בחירה ותנועה
        game.click(50, 50)
        game.click(150, 150)

        # המתנה של בדיוק 1000 מילישניות (או יותר) – זמן ההגעה המבוקש
        game.wait(1000)

        # כעת הכלי חייב לנחות רשמית בלוח ורשימת ההמתנה צריכה להתרוקן
        self.assertEqual(game.grid[1][1], "wK")
        self.assertEqual(game.grid[0][0], ".")
        self.assertEqual(len(game.pending_movements), 0)

    def test_consecutive_waits_trigger_arrival(self):
        grid = [
            ["wK", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]
        game = ChessGame(grid)

        game.click(50, 50)
        game.click(150, 150)

        # חלוקת ההמתנה למספר פעימות (למשל: 400ms ואז עוד 600ms)
        game.wait(400)
        self.assertEqual(game.grid[1][1], ".")  # עדיין בדרך

        game.wait(600)
        self.assertEqual(game.grid[1][1], "wK")  # הגיע ליעד בהצלחה (סך הכל 1000ms)
        self.assertEqual(game.grid[0][0], ".")


if __name__ == "__main__":
    unittest.main()