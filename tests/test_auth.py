import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DB.db_manager import DBManager
from application.auth.auth_handler import AuthHandler
from config.constants import DB_NAME

class MockAuthHandler(AuthHandler):
    """גרסת בדיקה העוקפת את הקלט מהמקלדת."""
    def __init__(self, username, password):
        super().__init__()
        self.mock_user = username
        self.mock_pass = password

    def login_mock(self):
        user_data = self.db.get_user_data(self.mock_user)
        if user_data:
            stored_password, elo = user_data
            if stored_password == self.mock_pass:
                return {"username": self.mock_user, "elo": elo}
        return None

def run_auth_test():
    # הכנה: יצירת משתמש בדיקה בבסיס הנתונים
    db = DBManager()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users (username, password, elo) VALUES (?, ?, ?)",
                     ("TestUser", "1234", 1200))
        conn.commit()

    # ביצוע הבדיקה
    tester = MockAuthHandler("TestUser", "1234")
    result = tester.login_mock()

    # אימות התוצאה
    assert result is not None
    assert result["username"] == "TestUser"
    assert result["elo"] == 1200
    print("Test 3 Passed: CLI Login logic verified successfully.")

if __name__ == "__main__":
    run_auth_test()