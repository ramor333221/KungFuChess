from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

logger = setup_logger("MoveLogger", "move_history.log")


class MoveLoggerObserver(Observer):
    """Observer responsible exclusively for logging completed moves."""

    def update(self, data):
        move_command = data.get("data")
        if move_command:
            logger.info(f"Recorded move: {move_command}")