import sqlite3
from config.constants import DB_NAME


class DBManager:
    """Handles centralized database operations for users and scores."""

    def __init__(self):
        self._initialize_tables()

    def _initialize_tables(self):
        """Creates tables for users and match history."""
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS users
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             username
                             TEXT
                             UNIQUE,
                             password
                             TEXT,
                             elo
                             INTEGER
                             DEFAULT
                             1200
                         )
                         """)
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS matches
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             winner_name
                             TEXT,
                             loser_name
                             TEXT,
                             timestamp
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)
            conn.commit()

    def update_user_elo(self, username, new_elo):
        """Updates the ELO rating for a specific user."""
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("UPDATE users SET elo = ? WHERE username = ?", (new_elo, username))
            conn.commit()

    def get_user_data(self, username):
        """Retrieves user info, including ELO."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT password, elo FROM users WHERE username = ?", (username,))
            return cursor.fetchone()