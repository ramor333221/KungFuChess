from src.core.controllers.interaction_controller import InteractionController
from src.core.controllers.movement_controller import MovementController
from src.core.engine.chess_rules_engine import ChessRulesEngine
from src.core.engine.game_status_manager import GameStatusManager
from src.core.exceptions.game_exceptions import BoardValidationError
from src.models.game_status import GameStatus, GameChronology
from src.core.validators.board_validator import BoardValidator


class GameRunner:
    """Manages game execution, board validation, and move processing."""

    def __init__(self):
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.engine = ChessRulesEngine()
        self.board = None
        self.movement_ctrl = None
        self.interaction_ctrl = None

    def run_game(self, raw_matrix, raw_commands):
        """Validates the board state and executes a sequence of game commands."""
        try:
            self.board = BoardValidator().validate(raw_matrix)
            if not self.board:
                return

            manager = GameStatusManager(self.board, self.status, self.chronology)
            self.movement_ctrl = MovementController(self.board, self.status, self.engine, manager)

            self.interaction_ctrl = InteractionController(self.movement_ctrl, self.board, self.status, manager)

            for command in raw_commands:
                if self.status.game_over:
                    break
                parts = command.split()
                if parts:
                    self.interaction_ctrl.execute_command(parts[0], parts[1:])

        except BoardValidationError as e:
            print(f"ERROR {e}")

    def get_possible_moves(self, row, col):
        """Retrieves all legal moves for a piece at the specified position."""
        if self.movement_ctrl is None:
            return []
        return self.movement_ctrl.get_legal_moves(row, col)