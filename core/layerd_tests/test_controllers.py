import unittest
from core.models.board_state import BoardState
from core.models.game_status import GameStatus, GameChronology
from core.engine.chess_rules_engine import ChessRulesEngine
from core.engine.game_status_manager import GameStatusManager
from core.controllers.interaction_controller import InteractionController
from core.controllers.movement_controller import MovementController


class TestControllers(unittest.TestCase):
    def setUp(self):
        # 4x4 test board
        raw_matrix = [
            [".", ".", ".", "."],
            [".", "wP", ".", "."],
            [".", "wN", ".", "."],
            [".", ".", ".", "."]
        ]
        self.board = BoardState(raw_matrix)
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.rules_engine = ChessRulesEngine()

        # Inject the new dependency
        self.status_manager = GameStatusManager(self.board, self.status, self.chronology)

        # Ensure MovementController and InteractionController receive all required dependencies
        self.movement_ctrl = MovementController(
            self.board, self.status, self.rules_engine, self.status_manager
        )
        self.interaction_ctrl = InteractionController(
            self.movement_ctrl, self.board, self.status, self.status_manager
        )

    def test_first_interaction_selects_piece(self):
        """Verify correct piece selection"""
        self.assertIsNone(self.status.selected_pos)

        # Use mapper to get center coordinates for (1, 1)
        x, y = self.interaction_ctrl.mapper.grid_to_pixel_center(1, 1)

        self.interaction_ctrl.execute_command("click", [str(x), str(y)])
        self.assertEqual(self.status.selected_pos, (1, 1))

    def test_legal_linear_move_schedules_movement(self):
        """Verify linear move scheduling"""
        self.status.selected_pos = (1, 1)
        self.movement_ctrl.execute_move((1, 1), (0, 1))

        self.assertIsNone(self.status.selected_pos)
        # Accessing the chronology as intended in the refactored architecture
        self.assertEqual(len(self.chronology.pending_movements), 1)
        self.assertEqual(self.chronology.pending_movements[0].piece_token, "wP")

    def test_legal_knight_move_schedules_airborne_movement(self):
        """Verify knight jump (airborne) scheduling"""
        self.movement_ctrl.set_airborne(True)
        self.movement_ctrl.execute_move((2, 1), (0, 2))

        self.assertIsNone(self.status.selected_pos)
        # Accessing the chronology as intended in the refactored architecture
        airborne_data = self.chronology.airborne_pieces[(0, 2)]
        self.assertEqual(airborne_data.movement.piece_token, "wN")


if __name__ == "__main__":
    unittest.main()