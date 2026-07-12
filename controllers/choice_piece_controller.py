# controllers/choice_piece_controller.py
from typing import Tuple
import config.constants as constants
from models.board_state import BoardState
from models.game_status import GameStatus
from engine.chess_rules_engine import ChessRulesEngine
from engine.game_status_manager import GameStatusManager


class ChoicePieceController:
    def __init__(self, board_state: BoardState, game_status: GameStatus,
                 rules_engine: ChessRulesEngine, status_manager: GameStatusManager):
        self._board = board_state
        self._status = game_status
        self._rules = rules_engine
        self._manager = status_manager
        self._next_move_is_airborne = False

    def set_next_move_airborne(self, is_airborne: bool) -> None:
        self._next_move_is_airborne = is_airborne

    def handle_cell_interaction(self, row: int, col: int) -> None:
        if self._status.game_over:
            return

        if not self._board.is_within_bounds(row, col):
            self._status.selected_pos = None
            self._next_move_is_airborne = False
            return

        current_time = self._status.game_clock_ms

        # חסימת תור דינמית: חוסמים פקודות חדשות אך ורק אם יש כלי שנמצא כרגע בתנועה אקטיבית באוויר או על הלוח
        active_linear = any(m.arrival_time_ms > current_time for m in self._status.pending_movements)
        active_airborne = any(data[1].arrival_time_ms > current_time for data in self._status.airborne_pieces.values())

        if active_linear or active_airborne:
            self._status.selected_pos = None
            self._next_move_is_airborne = False
            return

        # 1. אין כלי נבחר כרגע
        if self._status.selected_pos is None:
            if not self._board.is_empty(row, col):
                self._status.selected_pos = (row, col)
            return

        from_pos = self._status.selected_pos
        to_pos = (row, col)

        is_jump = self._next_move_is_airborne
        self._next_move_is_airborne = False
        self._status.selected_pos = None

        if from_pos == to_pos:
            return

        piece_token = self._board.get_token(from_pos[0], from_pos[1])
        if piece_token == constants.EMPTY_CELL:
            return

        # 2. החלפת בחירה בין כלים מאותו הצבע
        if not is_jump and not self._board.is_empty(row, col):
            clicked_piece = self._board.get_token(row, col)
            if clicked_piece != constants.EMPTY_CELL and piece_token[0] == clicked_piece[0]:
                self._status.selected_pos = (row, col)
                return

        # 3. בדיקת חוקיות הצעד ורישומו במערכת התנועות
        if self._rules.is_move_legal(self._board.matrix, self._status.moved_pieces, piece_token, from_pos, to_pos):
            if piece_token[1] == "N" or is_jump:
                self._manager.add_airborne_movement(from_pos, to_pos, piece_token)
            else:
                self._manager.add_linear_movement(from_pos, to_pos, piece_token)

            # פתרון מיידי של מהלכים שלוקחים 0ms (כדי שלא יחסמו את הפקודה הבאה שמתבצעת באותו מיליסנייה)
            self._manager.resolve_expired_movements()