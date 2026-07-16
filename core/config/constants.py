from typing import Set

# ==============================================================================
# UI & DISPLAY CONFIGURATIONS
# ==============================================================================
# Pixel dimensions for board grid cells (Used by BoardMapper and Controller)
GRID_SIZE = 8
CELL_SIZE = 80
HALF_CELL = CELL_SIZE // 2
SQUARE_PADDING = 3


# ==============================================================================
# SIMULATION & TIMING CONFIGURATIONS
# ==============================================================================
# Movement duration in milliseconds (Used by GameStatusManager)
MOVEMENT_DURATION_MS: int = 1000


# ==============================================================================
# DOMAIN MODELS & TOKEN DEFINITIONS
# ==============================================================================
# Represent an unoccupied board square
EMPTY_CELL: str = "."

# Supported piece colors and types (Used by InputValidator and RulesEngine)
VALID_COLORS: Set[str] = {"W", "B"}
VALID_PIECES: Set[str] = {"K", "Q", "R", "B", "N", "P"}


# ==============================================================================
# PARSING & I/O CONFIGURATIONS
# ==============================================================================
# Headers for parsing input streams (Used by BoardParser)
BOARD_HEADER: str = "Board:"
COMMANDS_HEADER: str = "Commands:"

PLAYER_WHITE=1
PLAYER_BLACK = 2