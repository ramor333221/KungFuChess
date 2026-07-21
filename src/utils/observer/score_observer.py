from config import constants


class ScoreObserver:
    """Observer responsible for updating player scores in the database upon game end."""
    def __init__(self, db_manager):
        self.db = db_manager

    def update(self, event, data):
        if event == constants.EVENT_GAME_OVER:
            winner = data.get("winner_name")
            loser = data.get("loser_name")
            if winner and loser:
                self.db.calculate_new_scores(winner, loser)