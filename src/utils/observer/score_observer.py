from src.utils.observer.observer import Observer


class ScoreObserver(Observer):
    """Observer responsible exclusively for updating player scores in the database."""
    def __init__(self, db_manager):
        self.db = db_manager

    def update(self, data):
        winner = data.get("winner_name")
        loser = data.get("loser_name")
        if winner and loser:
            self.db.calculate_new_scores(winner, loser)