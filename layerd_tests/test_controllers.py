# tests/test_controllers.py
import unittest
from models.board_state import BoardState
from models.game_status import GameStatus
from engine.chess_rules_engine import ChessRulesEngine
from engine.game_status_manager import GameStatusManager
from controllers.choice_piece_controller import ChoicePieceController
import config.constants as constants


class TestChoicePieceController(unittest.TestCase):
    def setUp(self):
        # Create a simple 4x4 layout for clean isolation
        raw_matrix = [
            [".", ".", ".", "."],
            [".", "wP", ".", "."],
            [".", "wN", ".", "."],
            [".", ".", ".", "."]
        ]
        self.board = BoardState(raw_matrix)
        self.status = GameStatus()
        self.rules_engine = ChessRulesEngine()
        self.status_manager = GameStatusManager(self.board, self.status)

        self.controller = ChoicePieceController(
            self.board, self.status, self.rules_engine, self.status_manager
        )

    def test_first_interaction_selects_piece(self):
        """Verifies clicking a tile with an active token highlights/selects it."""
        self.assertIsNone(self.status.selected_pos)

        # Click on the Pawn at (1, 1)
        self.controller.handle_cell_interaction(1, 1)

        self.assertEqual(self.status.selected_pos, (1, 1))

    def test_interaction_with_empty_cell_does_not_select(self):
        """Verifies clicking an empty square has no side-effects if no piece is selected."""
        self.controller.handle_cell_interaction(0, 0)
        self.assertIsNone(self.status.selected_pos)

    def test_out_of_bounds_click_resets_selection(self):
        """Verifies clicking beyond the board margins clears current selections safely."""
        # Pre-select the pawn
        self.status.selected_pos = (1, 1)

        # Click out of bounds
        self.controller.handle_cell_interaction(99, 99)
        self.assertIsNone(self.status.selected_pos)

    def test_legal_linear_move_clears_selection_and_schedules_movement(self):
        """Verifies a legal standard move clears selection and logs a pending linear trajectory."""
        # Pre-select the Pawn at (1, 1)
        self.status.selected_pos = (1, 1)

        # Move forward 1 step to (0, 1)
        self.controller.handle_cell_interaction(0, 1)

        # Selection state must reset
        self.assertIsNone(self.status.selected_pos)
        # Verify a sliding linear movement has been safely registered
        self.assertEqual(len(self.status.pending_movements), 1)
        self.assertEqual(self.status.pending_movements[0].piece_token, "wP")

    def test_legal_knight_move_schedules_airborne_movement(self):
        """Verifies a legal Knight interaction gets securely routed as a mid-air jump."""
        # Pre-select the Knight at (2, 1)
        self.status.selected_pos = (2, 1)

        # Execute valid L-shape jump to (0, 2)
        self.controller.handle_cell_interaction(0, 2)

        self.assertIsNone(self.status.selected_pos)
        # Linear track must stay empty, airborne map should hold the target destination
        self.assertEqual(len(self.status.pending_movements), 0)
        self.assertIn((0, 2), self.status.airborne_pieces)
        self.assertEqual(self.status.airborne_pieces[(0, 2)].piece_token, "wN")


if __name__ == "__main__":
    unittest.main()