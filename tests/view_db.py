import sqlite3
import os
from config.constants import DB_NAME


def view_db():
    # בדיקה אם הקובץ בכלל קיים בתיקייה הנוכחית
    if not os.path.exists(DB_NAME):
        print(f"Error: {DB_NAME} not found in this directory.")
        return

    try:
        with sqlite3.connect(DB_NAME) as conn:
            print("--- Users Table ---")
            cursor = conn.execute("SELECT * FROM users")
            for row in cursor.fetchall():
                print(row)

            print("\n--- Matches Table ---")
            cursor = conn.execute("SELECT * FROM matches")
            for row in cursor.fetchall():
                print(row)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    view_db()