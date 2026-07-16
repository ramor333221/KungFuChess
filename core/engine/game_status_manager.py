import heapq
from typing import Tuple
import core.config.constants as constants
from core.exceptions.game_exceptions import MovementError
from core.models.game_status import PendingMovement, AirborneMovement, AirborneSession, GameChronology
from core.models.interfaces import WritableBoard, WritableGameStatus

class GameStatusManager:
    """
    Manages the progression of time-based piece movements, resolving arrivals
    and updating the board state accordingly.
    """
    def __init__(self, board_state: WritableBoard, game_status: WritableGameStatus, chronology: GameChronology):
        self._board = board_state
        self._status = game_status
        self._chronology = chronology

    def process_time_tick(self, ms_elapsed: int) -> None:
        """
        Advances the game clock and triggers resolution for any movements
        that have reached their destination.
        """
        target_time = self._status.game_clock_ms + ms_elapsed
        while self._status.game_clock_ms < target_time:
            tick = min(1000, target_time - self._status.game_clock_ms)
            self._status.game_clock_ms += tick
            self.resolve_expired_movements()

    def add_airborne_movement(self, from_pos: Tuple[int, int], target_pos: Tuple[int, int], token: str) -> None:
        arrival = self._status.game_clock_ms + self._calculate_duration(from_pos, target_pos)
        # FIX: Access chronology instead of status
        self._chronology.airborne_pieces[target_pos] = AirborneSession(
            from_pos=from_pos,
            movement=AirborneMovement(token, arrival)
        )
        self._status.moved_pieces.add(from_pos)

    def resolve_expired_movements(self) -> None:
        now = self._status.game_clock_ms

        while self._chronology.pending_movements and self._chronology.pending_movements[0].arrival_time_ms <= now:
            m = heapq.heappop(self._chronology.pending_movements)
            self._land_piece(m.from_pos, m.to_pos, m.piece_token)

        expired_air = [p for p, s in self._chronology.airborne_pieces.items() if now >= s.movement.arrival_time_ms]
        for pos in expired_air:
            session = self._chronology.airborne_pieces.pop(pos)
            self._land_piece(session.from_pos, pos, session.movement.piece_token)

    def add_linear_movement(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], token: str) -> None:
        # FIX: Search chronology instead of status
        for move in self._chronology.pending_movements:
            if move.from_pos == from_pos:
                move.to_pos = to_pos
                move.arrival_time_ms = self._status.game_clock_ms + self._calculate_duration(from_pos, to_pos)
                heapq.heapify(self._chronology.pending_movements)
                return

        arrival = self._status.game_clock_ms + self._calculate_duration(from_pos, to_pos)
        heapq.heappush(self._chronology.pending_movements, PendingMovement(arrival, from_pos, to_pos, token))
        self._status.moved_pieces.add(from_pos)



    def _land_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], token: str) -> None:
        """
        Executes the final placement of a piece on the board, handling
        captures and promotions. Raises exceptions instead of silently returning.
        """
        r_f, c_f = int(from_pos[0]), int(from_pos[1])
        r_t, c_t = int(to_pos[0]), int(to_pos[1])

        target = self._board.get_token(r_t, c_t)

        # Check if target is not None and not empty before comparing
        if target and target != constants.EMPTY_CELL:
            if target[0] == token[0]:
                raise MovementError(f"Landing blocked by piece at {to_pos}")
            if target[1] == "K":
                self._status.game_over = True

        final_token = token
        if token[1] == "P" and (r_t == 0 or r_t == self._board.height - 1):
            final_token = f"{token[0]}Q"

        self._board.clear_cell(r_f, c_f)
        self._board.set_token(r_t, c_t, final_token)
        self._status.moved_pieces.discard(from_pos)

    def _calculate_duration(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> int:
        """
        Calculates movement duration based on Manhattan distance,
        ensuring a minimum of 1000ms.
        """
        dist = max(abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1]))
        return dist * 1000 if dist > 0 else 1000