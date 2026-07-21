import sqlite3
from pathlib import Path

from config.constants import DB_NAME


class DBManager:
    def __init__(self):
        # Set up the path inside the 'data' directory
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = str(self.data_dir / DB_NAME)

        self._create_table()

    def _create_table(self):
        """Creates the players table with password and score columns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS players
                         (
                             username
                             TEXT
                             PRIMARY
                             KEY,
                             password
                             TEXT,
                             score
                             INTEGER
                         )
                         """)

    def save_player_record(self, username, score, password=None):
        """
        Saves or updates a player's record.
        Includes password field if a new user is created.
        """
        with sqlite3.connect(self.db_path) as conn:
            if password:
                conn.execute("""
                             INSERT
                             OR IGNORE INTO players (username, password, score) VALUES (?, ?, ?)
                             """, (username, password, score))
            else:
                conn.execute("""
                             UPDATE players
                             SET score = ?
                             WHERE username = ?
                             """, (score, username))

    def get_player_score(self, username):
        """Retrieves the current score for a specific player."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT score FROM players WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else 1200

    def calculate_new_scores(self, winner_username, loser_username):
        """Calculates and updates score for the winner based on ELO ratio, leaving loser score unchanged."""
        winner_score = self.get_player_score(winner_username)
        loser_score = self.get_player_score(loser_username)

        score_diff = loser_score - winner_score
        gain = max(5, 10 + (score_diff // 2))

        self.save_player_record(winner_username, winner_score + gain)

        print(f"DEBUG: Winner {winner_username} updated with +{gain} points. Loser {loser_username} score unchanged.")

    def get_user_data(self, username):
        """Retrieves password and score for authentication."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, score FROM players WHERE username = ?", (username,))
            return cursor.fetchone()