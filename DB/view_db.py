import sqlite3
from pathlib import Path

from config.constants import DB_NAME


def view_data():
    # Point directly to the database file inside the 'data' directory
    db_path = Path("data") / DB_NAME

    if not db_path.exists():
        print("Database file not found or empty.")
        return

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players")
            rows = cursor.fetchall()

            print(f"{'Username':<20} | {'Score':<10}")
            print("-" * 35)
            for row in rows:
                print(f"{row[0]:<20} | {row[2]:<10}")
    except sqlite3.OperationalError:
        print("Database file not found or empty.")


if __name__ == "__main__":
    view_data()