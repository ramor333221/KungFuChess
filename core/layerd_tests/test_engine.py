import unittest
from core.exceptions.game_exceptions import MovementError
from core.models.board_state import BoardState
from core.models.game_status import GameStatus, GameChronology
from core.engine.chess_rules_engine import ChessRulesEngine
from core.engine.game_status_manager import GameStatusManager
import core.config.constants as constants


class TestChessRulesEngine(unittest.TestCase):
    def setUp(self):
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.engine = ChessRulesEngine()
        # Matrix: Rook at (3,0) moves to capture enemy 'bR' at (0,0).
        # (0,0) is 'bR', path (1,0) and (2,0) are empty.
        self.matrix = [
            ["bR", ".", ".", "bK"],
            [".", ".", ".", "."],
            [".", ".", ".", "."],
            ["wR", ".", ".", "wK"]
        ]
        self.moved_pieces = set()

    def test_rook_clear_path_capture(self):
        # Now passes because (0,0) is an enemy piece
        is_legal = self.engine.is_move_legal(
            self.matrix, self.moved_pieces, "wR", from_pos=(3, 0), to_pos=(0, 0)
        )
        self.assertTrue(is_legal)

    def test_king_invalid_stride(self):
        with self.assertRaises(MovementError):
            self.engine.is_move_legal(
                self.matrix, self.moved_pieces, "wK", from_pos=(3, 3), to_pos=(1, 3)
            )

    def test_rook_blocked_path(self):
        # Path blocked by "wP" at (2,0)
        self.matrix[2][0] = "wP"
        with self.assertRaises(MovementError):
            self.engine.is_move_legal(
                self.matrix, self.moved_pieces, "wR", from_pos=(3, 0), to_pos=(0, 0)
            )


class TestGameStatusManager(unittest.TestCase):
    def setUp(self):
        raw_matrix = [[".", ".", "."], [".", "wP", "."], [".", ".", "."]]
        self.board = BoardState(raw_matrix)
        self.status = GameStatus()
        self.chronology = GameChronology()
        self.manager = GameStatusManager(self.board, self.status, self.chronology)

    def test_linear_movement_scheduling(self):
        from_pos = (1, 1)
        to_pos = (2, 2)
        piece = "wP"
        self.manager.add_linear_movement(from_pos, to_pos, piece)

        self.assertIn(from_pos, self.status.moved_pieces)
        self.assertEqual(len(self.chronology.pending_movements), 1)

    def test_time_tick_resolves_landing_with_promotion(self):
        from_pos = (1, 1)
        to_pos = (2, 2)
        piece = "wP"
        self.manager.add_linear_movement(from_pos, to_pos, piece)
        self.manager.process_time_tick(constants.MOVEMENT_DURATION_MS)
        self.assertEqual(self.board.get_token(2, 2), "wQ")

    def test_airborne_capture_only_enemy(self):
        # Setup: wK at (1,0), bR (enemy) at (1,1)
        raw_matrix = [
            [".", ".", "."],
            ["wK", "bR", "."],
            [".", ".", "."]
        ]
        self.board = BoardState(raw_matrix)
        # Use existing manager, but reset board
        self.manager._land_piece((1, 0), (1, 1), "wK")
        self.assertEqual(self.board.get_token(1, 1), "wK")
        self.assertEqual(self.board.get_token(1, 0), constants.EMPTY_CELL)


if __name__ == "__main__":
    unittest.main()