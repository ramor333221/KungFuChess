import logging
from core.exceptions.game_exceptions import ValidationError, MovementError

logger = logging.getLogger(__name__)

def handle_game_error(error: Exception):
    """
    Processes errors using the logging module.
    """
    if isinstance(error, ValidationError):
        logger.warning(f"CONFIGURATION_ERROR: {error}")
    elif isinstance(error, MovementError):
        logger.info(f"MOVE_DENIED: {error}")
    else:
        logger.error(f"SYSTEM_ERROR: {error}", exc_info=True)