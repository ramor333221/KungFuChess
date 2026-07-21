from config import constants
from src.utils.observer.observer import Observer
from src.utils.logger.logger import setup_logger

logger = setup_logger("MoveLogger", "move_history.log")


class MoveLoggerObserver(Observer):
    """Observer responsible for logging or processing move events."""

    def update(self, event, data):
        """Processes move completion events."""
        if event == constants.EVENT_MOVE_COMPLETED:
            move_command = data.get("data")
            if move_command:
                logger.info(f"Recorded move: {move_command}")