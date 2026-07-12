# tests/test_engine.py
import unittest
from models.board_state import BoardState
from models.game_status import GameStatus
from engine.chess_rules_engine import ChessRulesEngine
from engine.game_status_manager import GameStatusManager
import config.constants as constants


class TestChessRulesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ChessRulesEngine()
        self.matrix = [
            ["bR", ".", ".", "bK"],
            [".", "wP", ".", "."],
            [".", ".", ".", "."],
            ["wR", ".", ".", "wK"]
        ]
        self.moved_pieces = set()

    def test_rook_blocked_path(self):
        self.matrix[2][0] = "wP"
        is_legal = self.engine.is_move_legal(
            self.matrix, self.moved_pieces, "wR", from_pos=(3, 0), to_pos=(0, 0)
        )
        self.assertFalse(is_legal)

    def test_rook_clear_path_capture(self):
        is_legal = self.engine.is_move_legal(
            self.matrix, self.moved_pieces, "wR", from_pos=(3, 0), to_pos=(0, 0)
        )
        self.assertTrue(is_legal)

    def test_king_invalid_stride(self):
        is_legal = self.engine.is_move_legal(
            self.matrix, self.moved_pieces, "wK", from_pos=(3, 3), to_pos=(1, 3)
        )
        self.assertFalse(is_legal)


class TestGameStatusManager(unittest.TestCase):
    def setUp(self):
        raw_matrix = [
            [".", ".", "."],
            [".", "wP", "."],
            [".", ".", "."]
        ]
        self.board = BoardState(raw_matrix)
        self.status = GameStatus()
        self.manager = GameStatusManager(self.board, self.status)

    def test_linear_movement_scheduling(self):
        from_pos = (1, 1)
        to_pos = (2, 2)
        piece = "wP"

        self.manager.add_linear_movement(from_pos, to_pos, piece)
        self.assertEqual(self.board.get_token(1, 1), constants.EMPTY_CELL)
        self.assertEqual(len(self.status.pending_movements), 1)
        self.assertEqual(self.status.pending_movements[0].piece_token, "wP")
        self.assertIn(from_pos, self.status.moved_pieces)

    def test_time_tick_resolves_landing_with_promotion(self):
        from_pos = (1, 1)
        to_pos = (2, 2)
        piece = "wP"

        self.manager.add_linear_movement(from_pos, to_pos, piece)

        self.manager.process_time_tick(constants.MOVEMENT_DURATION_MS - 1)
        self.assertEqual(self.board.get_token(2, 2), constants.EMPTY_CELL)

        self.manager.process_time_tick(1)
        self.assertEqual(self.board.get_token(2, 2), "wQ")
        self.assertEqual(len(self.status.pending_movements), 0)

    def test_airborne_capture_only_enemy(self):
        # 1. Setup board: . . ., wK bR ., . . .
        raw_matrix = [
            [".", ".", "."],
            ["wK", "bR", "."],
            [".", ".", "."]
        ]
        self.board = BoardState(raw_matrix)
        self.status = GameStatus()
        self.manager = GameStatusManager(self.board, self.status)

        # 2. Command sequence: jump 50 150 (jump wK from 1,0 to 1,1)
        # 150 pixels / 100 per cell = col 1.5 -> grid 1. Note: 50 is row 0.5 -> 0.
        # Let's use the grid positions directly for the engine:
        from_pos = (1, 0)  # wK
        target_pos = (1, 1)  # bR

        # Add airborne movement
        self.manager.add_airborne_movement(from_pos, target_pos, "wK")

        # Simulate clicks (in a real scenario, click updates status.selected_pos)
        # Here we directly trigger the landing of wK on the bR cell
        self.manager._land_piece(from_pos, target_pos, "wK", is_airborne_landing=True)

        # 3. Assertions
        # wK should be at (1,1), (1,0) should be empty, bR should be gone
        self.assertEqual(self.board.get_token(1, 1), "wK")
        self.assertEqual(self.board.get_token(1, 0), constants.EMPTY_CELL)
        self.assertEqual(self.board.get_token(0, 1), constants.EMPTY_CELL)  # Top middle

if __name__ == "__main__":
    unittest.main()