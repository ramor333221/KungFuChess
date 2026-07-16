# models/game_status.py
import heapq
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set, Optional

from core.config import constants


@dataclass
class AirborneMovement:
    """
    Data container tracking a piece that has been temporarily launched/suspended in mid-air.
    """
    piece_token: str
    arrival_time_ms: int

@dataclass
class AirborneSession:
    """Wrapper to maintain state for pieces in mid-air."""
    from_pos: Tuple[int, int]
    movement: AirborneMovement

@dataclass(order=True)
class PendingMovement:
    """
    Data container tracking a standard sliding piece.
    arrival_time_ms is placed first to ensure priority sorting.
    """
    arrival_time_ms: int
    from_pos: Tuple[int, int] = field(compare=False)
    to_pos: Tuple[int, int] = field(compare=False)
    piece_token: str = field(compare=False)

@dataclass
class GameChronology:
    """
    Handles the simulation timeline, separating event scheduling
    from core game state properties.
    """
    pending_movements: List[PendingMovement] = field(default_factory=list)
    airborne_pieces: Dict[Tuple[int, int], AirborneSession] = field(default_factory=dict)


@dataclass
class GameStatus:
    game_clock_ms: int = 0
    game_over: bool = False
    _selected_pos: Optional[Tuple[int, int]] = None
    moved_pieces: Set[Tuple[int, int]] = field(default_factory=set)

    # Track turn using constants
    current_turn: int = constants.PLAYER_WHITE

    # New tracking fields
    scores: Dict[int, int] = field(default_factory=lambda: {constants.PLAYER_WHITE: 0, constants.PLAYER_BLACK: 0})
    command_history: List[str] = field(default_factory=list)

    @property
    def selected_pos(self) -> Optional[Tuple[int, int]]:
        return self._selected_pos

    @selected_pos.setter
    def selected_pos(self, value: Optional[Tuple[int, int]]) -> None:
        self._selected_pos = value

    def switch_turn(self):
        self.current_turn = (
            constants.PLAYER_BLACK if self.current_turn == constants.PLAYER_WHITE
            else constants.PLAYER_WHITE
        )

    def update_score(self, player_id: int, points: int):
        self.scores[player_id] += points

    def add_history(self, command: str):
        self.command_history.append(command)





