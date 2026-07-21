import cv2
from typing import Set

# ==============================================================================
# GRID & BOARD
# ==============================================================================
GRID_SIZE = 8
CELL_SIZE = 80
HALF_CELL = CELL_SIZE // 2
SQUARE_PADDING = 3
EMPTY_CELL: str = "."
BOARD_SIZE = 8

# ==============================================================================
# GAME LOGIC & PLAYERS
# ==============================================================================
PLAYER_WHITE = 0
PLAYER_BLACK = 1
VALID_COLORS: Set[str] = {"W", "B"}
VALID_PIECES: Set[str] = {"K", "Q", "R", "B", "N", "P"}
MOVEMENT_DURATION_MS: int = 1000

# ==============================================================================
# UI RENDERER: COLORS (BGR)
# ==============================================================================
COLOR_SIDEBAR_BG = (40, 40, 40)
COLOR_TEXT_CYAN = (0, 255, 255)
COLOR_TEXT_YELLOW = (200, 200, 0)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_GRAY = (150, 150, 150)
COLOR_HISTORY_TEXT = (200, 200, 200)
COLOR_BTN_BG = (100, 100, 100)
COLOR_WINNER_RED = (0, 0, 255)
COLOR_MOVE_VALID = (0, 255, 0)

# ==============================================================================
# UI RENDERER: FONTS & SCALING
# ==============================================================================
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_TINY = 0.4
FONT_SCALE_SMALL = 0.4
FONT_SCALE_MEDIUM = 0.5
FONT_SCALE_LARGE = 0.6
FONT_SCALE_XLARGE = 0.7
FONT_SCALE_TITLE = 1.0
FONT_SCALE_HEADER = 1.2

THICKNESS_THIN = 1
THICKNESS_MEDIUM = 2
THICKNESS_BOLD = 3

PIECE_SIZE_MULTIPLIER = 0.8
VALID_MOVE_RADIUS_DIV = 4

# ==============================================================================
# UI LAYOUT: SIDEBAR & BUTTONS
# ==============================================================================
SIDEBAR_WIDTH = 300
SIDEBAR_PADDING_X = 50
SIDEBAR_TEXT_X = 20

# Buttons
SWITCH_BTN_W = 200
SWITCH_BTN_H = 50
SWITCH_BTN_Y = 600
SWITCH_TEXT_X = 30
SWITCH_TEXT_Y = 35

NEW_GAME_BTN_X = 250
NEW_GAME_BTN_Y = 500
NEW_GAME_BTN_W = 300
NEW_GAME_BTN_H = 100

# History & Status
HISTORY_MAX_Y = 580
STATUS_Y = 30
SCORES_Y = 70
SCORE_VAL_Y = 100
SCORE_OFFSET_Y = 30
HISTORY_Y = 190
NAME_Y = 220
MOVE_START_Y = 240
MOVE_DY = 25
HISTORY_TEXT_OFFSET_Y = 25
HISTORY_COL_WHITE = 10
HISTORY_COL_BLACK = 150

# Game Over Overlay
GAME_OVER_OFFSET_X = 120
GAME_OVER_OFFSET_Y = 50
NEW_GAME_MSG_Y = 60
GAME_OVER_TEXT_X_OFFSET = 110
GAME_OVER_TEXT_Y_OFFSET = 10
GAME_OVER_TITLE_X = 120
GAME_OVER_TITLE_Y = 50

# ==============================================================================
# I/O HEADERS
# ==============================================================================
BOARD_HEADER: str = "Board:"
COMMANDS_HEADER: str = "Commands:"


# ==============================================================================
# SOCKET
# ==============================================================================
# System Configuration
SERVER_PORT = 8765
TIMEOUT_SECONDS = 20
GRID_SIZE = 8
EMPTY_CELL = None
MATCHMAKING_TIMEOUT = 60
ELO_DIFFERENCE_THRESHOLD = 100
MSG_TYPE_MOVE = "MOVE"

# Players
PLAYER_WHITE = "White"
PLAYER_BLACK = "Black"

# Database
DB_NAME = "chess_scores.db"
EVENT_MOVE_COMPLETED = "move_completed"
EVENT_GAME_OVER = "game_over"


# Pub-Sub Topics for Network/Server Communication
TOPIC_PLAYER_MOVE = "player_move"
TOPIC_OPPONENT_MOVE = "opponent_move"
TOPIC_SERVER_ALERT = "server_alert"
