from pathlib import Path

import cv2
from typing import Set

# ==============================================================================
# GRID & BOARD
# ==============================================================================
GRID_SIZE = 8
BOARD_SIZE = 8
BOARD_MAX_INDEX = GRID_SIZE - 1
CELL_SIZE = 80
HALF_CELL = CELL_SIZE // 2
SQUARE_PADDING = 3
EMPTY_CELL = None

# ==============================================================================
# GAME LOGIC & PLAYERS
# ==============================================================================
PLAYER_WHITE = 0
PLAYER_BLACK = 1
VALID_COLORS: Set[str] = {"W", "B"}
VALID_PIECES: Set[str] = {"K", "Q", "R", "B", "N", "P"}
MOVEMENT_DURATION_MS: int = 1000
ATTR_GAME_OVER = "game_over"

COLOR_WHITE = "white"
COLOR_BLACK = "black"
COLOR_VIEWER = "viewer"
PIECE_WHITE_INDICATOR = "W"
PIECE_BLACK_INDICATOR = "B"
DEFAULT_PLAYER_NAME = "Player"
DEFAULT_MODE = "auto"
DISCONNECT_TIMEOUT_SECONDS = 20

# ==============================================================================
# PORTAL & GUI WINDOWS
# ==============================================================================
PORTAL_WINDOW_WIDTH = 340
PORTAL_WINDOW_HEIGHT = 320
DEFAULT_ENTRY_WIDTH = 28
DEFAULT_BUTTON_WIDTH = 9
DEFAULT_USERNAME = "Player1"

ACTION_CANCEL = "CANCEL"
ACTION_CREATE = "CREATE"
ACTION_JOIN = "JOIN"

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

PIECE_ANIMATION_SCALE = 0.65
TEXT_FONT_SCALE_LARGE = 0.8
TEXT_FONT_SCALE_MEDIUM = 0.6
TEXT_THICKNESS = 2

WELCOME_TITLE_TEXT = "Welcome to Chess"
UI_FONT_FAMILY = "Arial"
UI_TITLE_FONT_SIZE = 14
UI_TITLE_PADY = 8

# ==============================================================================
# TIMING & ANIMATION
# ==============================================================================
DEFAULT_DISCONNECT_COUNTDOWN = 20
ONE_SECOND_MS = 1000
FRAME_SLEEP_SECONDS = 0.01
EXIT_DELAY_SECONDS = 3

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
COMMAND_CLICK = "click"

# ==============================================================================
# SOCKET & NETWORK
# ==============================================================================
SERVER_PORT = 8765
DEFAULT_WS_URI = "ws://localhost:8765"
DEFAULT_ELO = 1200
UNKNOWN_OPPONENT = "Unknown_Opponent"
TIMEOUT_SECONDS = 20
MATCHMAKING_TIMEOUT = 60
ELO_DIFFERENCE_THRESHOLD = 100
TRIAL=1
MAX_TRIAL=5
RECONNECT_BACKOFF_SECONDS = 3

MSG_TYPE_LOGIN = "LOGIN"
MSG_TYPE_MOVE = "MOVE"
MSG_TYPE_START = "START"
MSG_TYPE_START_VIEWER = "START_VIEWER"
MSG_TYPE_ROOM_CREATED = "ROOM_CREATED"
MSG_TYPE_OPPONENT_DISCONNECTED = "OPPONENT_DISCONNECTED"
MSG_TYPE_DISCONNECT = "DISCONNECT"
MSG_TYPE_WIN_BY_TIMEOUT = "WIN_BY_TIMEOUT"
MSG_TYPE_ERROR = "ERROR"

PROJECT_ROOT = Path("C:/Users/User/Downloads/Kung Fu Chess")
ASSETS_PATH = PROJECT_ROOT / "assests"
SERVER_HOST = "0.0.0.0"
SERVER_URI = f"ws://{SERVER_HOST}:{SERVER_PORT}"

# ==============================================================================
# DATABASE & EVENTS
# ==============================================================================
DB_NAME = "chess_scores.db"
EVENT_MOVE_COMPLETED = "move_completed"
EVENT_GAME_OVER = "game_over"

# ==============================================================================
# PUB-SUB TOPICS
# ==============================================================================
TOPIC_PLAYER_MOVE = "player_move"
TOPIC_OPPONENT_MOVE = "opponent_move"
TOPIC_SERVER_ALERT = "server_alert"

TEXT_OFFSET_X = 20
TEXT_ROOM_Y = 40
TEXT_DISCONNECT_Y = 80
CV_WAIT_KEY_DELAY = 1
DISCONNECT_INACTIVE_STATE = -1
MS_PER_SECOND = 1000
KEY_MASK_8BIT = 0xFF
QUIT_KEY_CHAR = 'q'