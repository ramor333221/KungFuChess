from core.controllers.interaction_controller import InteractionController
from core.controllers.movement_controller import MovementController
from core.engine.chess_rules_engine import ChessRulesEngine
from core.engine.game_status_manager import GameStatusManager
from core.exceptions.game_exceptions import BoardValidationError
from core.models.game_status import GameStatus, GameChronology
from core.validators.board_validator import BoardValidator


# core/game_runner.py

class GameRunner:
    def __init__(self):
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.engine = ChessRulesEngine()
        self.board = None
        self.movement_ctrl = None
        self.interaction_ctrl = None

    def run_game(self, raw_matrix, raw_commands):
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
        if self.movement_ctrl is None:
            return []
        return self.movement_ctrl.get_legal_moves(row, col)