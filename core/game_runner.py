from core.controllers.interaction_controller import InteractionController
from core.controllers.movement_controller import MovementController
from core.validators.board_validator import BoardValidator
from core.models.game_status import GameStatus, GameChronology
from core.engine.chess_rules_engine import ChessRulesEngine
from core.engine.game_status_manager import GameStatusManager
from core.exceptions.game_exceptions import BoardValidationError

class GameRunner:
    def __init__(self):
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.engine = ChessRulesEngine()
        self.board = None

    def run_game(self, raw_matrix, raw_commands):
        try:
            self.board = BoardValidator().validate(raw_matrix)
            if not self.board:
                return

            manager = GameStatusManager(self.board, self.status, self.chronology)
            movement_ctrl = MovementController(self.board, self.status, self.engine, manager)
            interaction_ctrl = InteractionController(movement_ctrl, self.board, self.status, manager)

            for command in raw_commands:
                if self.status.game_over:
                    break
                parts = command.split()
                if parts:
                    interaction_ctrl.execute_command(parts[0], parts[1:])

        except BoardValidationError as e:
            print(f"ERROR {e}")

if __name__ == "__main__":
    print("--- Core Module Debug Mode ---")
    test_matrix = []
    test_commands = []

    runner = GameRunner()
    runner.run_game(test_matrix, test_commands)


#python -m core.game_runner