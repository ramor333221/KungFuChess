from typing import Set

# ==============================================================================
# UI & DISPLAY CONFIGURATIONS
# ==============================================================================
# Pixel dimensions for board grid cells (Used by BoardMapper and Controller)
CELL_SIZE: int = 100


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