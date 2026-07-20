import sqlite3
from config.constants import DB_NAME

def initialize_db():
    """Creates the database file and initializes the scores table."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    winner_name TEXT,
                    loser_name TEXT,
                    winner_elo INTEGER,
                    loser_elo INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print(f"Database '{DB_NAME}' created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    initialize_db()