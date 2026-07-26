from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

achievement_logger = setup_logger("AchievementLogger", "achievements.log")


class AchievementObserver(Observer):
    """Observer responsible exclusively for granting player achievements."""

    def update(self, data):
        winner_name = data.get("winner_name")
        if winner_name:
            achievement_logger.info(f"Achievement unlocked: Victory achieved by {winner_name}")