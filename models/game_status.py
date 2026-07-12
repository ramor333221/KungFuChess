# models/game_status.py
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set


@dataclass
class PendingMovement:
    """
    Data container tracking a standard sliding piece currently traveling to its target square.
    """
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    piece_token: str
    arrival_time_ms: int


@dataclass
class AirborneMovement:
    """
    Data container tracking a piece that has been temporarily launched/suspended in mid-air.
    """
    piece_token: str
    arrival_time_ms: int


@dataclass
class GameStatus:
    """
    Main data container holding the live, mutable parameters of an active game session.
    """
    game_clock_ms: int = 0
    game_over: bool = False
    selected_pos: Tuple[int, int] = None

    # Active linear movements currently underway toward their destinations
    pending_movements: List[PendingMovement] = field(default_factory=list)

    # Tracks currently airborne elements mapped by their landing grid index, e.g., {(row, col): AirborneMovement}
    airborne_pieces: Dict[Tuple[int, int], AirborneMovement] = field(default_factory=dict)

    # Keeps track of coordinates of components that have completed at least one movement
    moved_pieces: Set[Tuple[int, int]] = field(default_factory=set)