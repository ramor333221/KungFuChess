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
        for move in self._chronology.pending_movements:
            if move.from_pos == from_pos:
                move.to_pos = to_pos
                move.arrival_time_ms = self._status.game_clock_ms + self._calculate_duration(from_pos, to_pos)
                heapq.heapify(self._chronology.pending_movements)
                return

        arrival = self._status.game_clock_ms + self._calculate_duration(from_pos, to_pos)
        heapq.heappush(self._chronology.pending_movements, PendingMovement(arrival, from_pos, to_pos, token))
        self._status.moved_pieces.add(from_pos)

    def _land_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece_token: str):
        """
        Finalizes movement, handles King captures, and keeps states in sync.
        """
        matrix = self._board.matrix
        status = self._status

        if not (0 <= to_pos[0] < constants.GRID_SIZE and 0 <= to_pos[1] < constants.GRID_SIZE):
            print(f"CRITICAL: Land attempt out of bounds: {to_pos}")
            return

        target_token = matrix[to_pos[0]][to_pos[1]]
        if target_token and "K" in target_token:
            status.game_over = True
            status.winner = "White" if "W" in piece_token else "Black"
            print(f"GAME OVER! {status.winner} wins by capturing {target_token}")

        matrix[from_pos[0]][from_pos[1]] = constants.EMPTY_CELL
        matrix[to_pos[0]][to_pos[1]] = piece_token

        if hasattr(status, 'piece_states'):
            if from_pos in status.piece_states:
                del status.piece_states[from_pos]
            status.piece_states[to_pos] = "idle"

    def _calculate_duration(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> int:
        """
        Calculates movement duration based on Manhattan distance,
        ensuring a minimum of 1000ms.
        """
        dist = max(abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1]))
        return dist * 1000 if dist > 0 else 1000