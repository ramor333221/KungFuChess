from config import constants
from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

achievement_logger = setup_logger("AchievementLogger", "achievements.log")


class AchievementObserver(Observer):
    """Observer responsible for tracking game events and granting player achievements."""

    def update(self, event, data):
        """Processes events to check for achievement conditions."""
        if event == constants.EVENT_GAME_OVER:
            winner_name = data.get("winner_name")
            if winner_name:
                achievement_logger.info(f"Achievement unlocked: Victory achieved by {winner_name}")