import sqlite3
import os
from DB.db_manager import DBManager
from config.constants import DB_NAME


def run_tests():
    # 1. Cleanup
    # if os.path.exists(DB_NAME):
    #     os.remove(DB_NAME)

    db = DBManager()
    print("Test 1: Database initialized successfully.")

    # 2. Test User Registration (Manual Insert for test)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO users (username, password, elo) VALUES (?, ?, ?)",
                     ("PlayerOne", "pass123", 1200))
        conn.execute("INSERT INTO users (username, password, elo) VALUES (?, ?, ?)",
                     ("PlayerTwo", "pass456", 1200))
    print("Test 2: Users added.")

    # 3. Test ELO Update
    db.update_user_elo("PlayerOne", 1250)
    user_data = db.get_user_data("PlayerOne")
    assert user_data[1] == 1250
    print("Test 3: ELO update successful (Value: 1250).")

    # 4. Test Match Recording
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO matches (winner_name, loser_name) VALUES (?, ?)",
                     ("PlayerOne", "PlayerTwo"))
        cursor = conn.execute("SELECT * FROM matches")
        record = cursor.fetchone()
        assert record[1] == "PlayerOne"
    print("Test 4: Match record stored correctly.")

    print("\n--- All tests passed! System is ready. ---")


if __name__ == "__main__":
    run_tests()