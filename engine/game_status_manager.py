# engine/game_status_manager.py
from typing import List, Tuple
import config.constants as constants
from models.board_state import BoardState
from models.game_status import GameStatus, PendingMovement, AirborneMovement


class GameStatusManager:
    def __init__(self, board_state: BoardState, game_status: GameStatus):
        self._board = board_state
        self._status = game_status

    def process_time_tick(self, ms_elapsed: int) -> None:
        target_time = self._status.game_clock_ms + ms_elapsed

        while self._status.game_clock_ms < target_time:
            next_tick = min(1000, target_time - self._status.game_clock_ms)
            self._status.game_clock_ms += next_tick
            self.resolve_expired_movements()

    def _calculate_duration(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> int:
        distance = max(abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1]))
        return distance * 1000 if distance > 0 else 1000

    def add_linear_movement(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_token: str) -> None:
        duration = self._calculate_duration(from_pos, to_pos)
        arrival = self._status.game_clock_ms + duration
        movement = PendingMovement(from_pos, to_pos, piece_token, arrival)

        self._status.pending_movements.append(movement)
        self._status.moved_pieces.add(from_pos)
        # לא מוחקים כאן את כלי המקור! הוא נשאר על הלוח עד ההגעה.

    def add_airborne_movement(self, from_pos: Tuple[int, int], target_pos: Tuple[int, int], piece_token: str) -> None:
        duration = self._calculate_duration(from_pos, target_pos)
        arrival = self._status.game_clock_ms + duration
        airborne = AirborneMovement(piece_token, arrival)

        self._status.airborne_pieces[target_pos] = (from_pos, airborne)
        self._status.moved_pieces.add(from_pos)
        # לא מוחקים כאן את כלי המקור!

    def resolve_expired_movements(self) -> None:
        current_time = self._status.game_clock_ms

        # 1. עיבוד תנועות ליניאריות שהסתיימו
        self._status.pending_movements.sort(key=lambda x: x.arrival_time_ms)
        remaining_linear = []
        for move in self._status.pending_movements:
            if current_time >= move.arrival_time_ms:
                self._land_piece(move.from_pos, move.to_pos, move.piece_token, is_airborne_landing=False)
            else:
                remaining_linear.append(move)
        self._status.pending_movements = remaining_linear

        # 2. עיבוד כלים מעופפים (Airborne) שנוחתים
        remaining_airborne = {}
        for target_pos, data in sorted(self._status.airborne_pieces.items(),
                                       key=lambda item: item[1][1].arrival_time_ms):
            from_pos, air_move = data
            if current_time >= air_move.arrival_time_ms:
                self._land_piece(from_pos, target_pos, air_move.piece_token, is_airborne_landing=True)
            else:
                remaining_airborne[target_pos] = data
        self._status.airborne_pieces = remaining_airborne

    def _land_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_token: str,
                    is_airborne_landing: bool) -> None:
        r, c = to_pos
        current_time = self._status.game_clock_ms

        # 1. Validation: Check for other airborne pieces that aren't the one we are moving
        has_active_airborne_over_cell = False
        if to_pos in self._status.airborne_pieces:
            origin_pos, air_move = self._status.airborne_pieces[to_pos]
            if air_move.arrival_time_ms > current_time and origin_pos != from_pos:
                has_active_airborne_over_cell = True

        # Abort if the landing square is blocked by another piece in the air
        if not is_airborne_landing and has_active_airborne_over_cell:
            return

        # 2. Prevent self-trampling
        target_token = self._board.get_token(r, c)
        if target_token != constants.EMPTY_CELL and target_token[0] == piece_token[0]:
            return

        # 3. Execution (Atomic Commitment)

        # Clear the source square
        if self._board.get_token(from_pos[0], from_pos[1]) == piece_token:
            self._board.clear_cell(from_pos[0], from_pos[1])

        # If we are landing on a cell that has an active airborne piece,
        # remove it from the tracking dictionary to process the capture.
        if to_pos in self._status.airborne_pieces:
            del self._status.airborne_pieces[to_pos]

        # Handle Capture Logic
        # We need to re-fetch the target in case the board state changed
        # (e.g., if it was an airborne piece being removed)
        actual_target = self._board.get_token(r, c)

        if actual_target != constants.EMPTY_CELL:
            if actual_target[0] != piece_token[0]:
                if actual_target[1] == "K":
                    self._status.game_over = True
                # If there's an enemy piece, we don't need to do anything
                # special, set_token will overwrite it.

        # Handle Pawn promotion
        final_piece_token = piece_token
        if piece_token[1] == "P" and (r == 0 or r == self._board.height - 1):
            final_piece_token = f"{piece_token[0]}Q"

        # Finalize the move
        self._board.set_token(r, c, final_piece_token)