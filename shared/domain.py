"""
Core domain models representing business logic entities ('hero' data structures)
independent of UI strings or network transport layers.
"""
from dataclasses import dataclass


@dataclass
class MoveCommand:
    """Strongly-typed domain object representing chess move coordinates."""
    from_row: int
    from_col: int
    to_row: int
    to_col: int
