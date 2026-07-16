class GameError(Exception):
    """Base class for all game exceptions."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class BoardValidationError(GameError):
    """Errors related to board structure or token definitions."""
    pass

class MovementError(GameError):
    """Errors related to illegal moves."""
    pass

class LogicError(GameError):
    """Errors related to game state transitions."""
    pass

class ValidationError(GameError):
    """General validation errors."""
    pass