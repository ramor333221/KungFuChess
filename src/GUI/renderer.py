from pathlib import Path
import time
import cv2

from config import constants
from config.constants import ASSETS_PATH
from src.utils.UI.animation_manager import AnimationManager


class Renderer:
    """Renders the game board, pieces, valid moves, and side panel UI elements with corrected column orientation for history."""

    def __init__(self, facade, player_color='white'):
        """Initializes the renderer with the facade, player color configuration, and dynamic asset loading."""
        self.facade = facade
        self.player_color = player_color
        self.btn_switch_w = constants.SWITCH_BTN_W
        self.btn_switch_h = constants.SWITCH_BTN_H
        self.btn_switch_y = constants.SWITCH_BTN_Y
        self.btn_switch_x = 0

        self.piece_animations = {}
        self._load_animations()

    def _load_animations(self):
        """Dynamically load animated piece sprites and config files safely."""
        project_root = Path(__file__).resolve().parent.parent.parent

        if ASSETS_PATH and ASSETS_PATH.exists():
            asset_dir = ASSETS_PATH.parent if ASSETS_PATH.is_file() else ASSETS_PATH
            base_path = asset_dir / "piece_mine"
        else:
            base_path = project_root / "assests" / "piece_mine"

        if base_path.exists():
            for folder in base_path.iterdir():
                if folder.is_dir():
                    piece_code = folder.name

                    # Ensure config.json exists at the root of the piece folder for AnimationManager
                    root_config = folder / "config.json"
                    if not root_config.exists():
                        sub_configs = list(folder.glob("**/config.json"))
                        if sub_configs:
                            import shutil
                            try:
                                shutil.copy(sub_configs[0], root_config)
                            except Exception:
                                pass

                    if root_config.exists():
                        try:
                            # Pass the root piece folder to AnimationManager
                            manager = AnimationManager(folder)

                            # Fixed: Use constants.CELL_SIZE instead of DEFAULT_CELL_SIZE
                            cell_size = getattr(self.facade.mapper, 'cell_size', constants.CELL_SIZE)
                            scale = getattr(constants, 'PIECE_ANIMATION_SCALE', 1.0)
                            size = int(cell_size * scale)

                            for frame in manager.frames:
                                if hasattr(frame, 'img') and frame.img is not None:
                                    frame.img = cv2.resize(frame.img, (size, size), interpolation=cv2.INTER_AREA)

                            self.piece_animations[piece_code] = manager
                        except Exception as e:
                            print(f"DEBUG: Error loading animation for '{piece_code}': {e}")

    def render(self, base_img, piece_animations, selected_square):
        """Renders the complete game canvas including board, pieces, and sidebar information."""
        canvas = cv2.copyMakeBorder(base_img, 0, 0, 0, constants.SIDEBAR_WIDTH,
                                    cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
        if canvas.shape[2] == 3:
            canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2BGRA)

        board_w = base_img.shape[1]
        self.btn_switch_x = board_w + constants.SIDEBAR_PADDING_X

        self._draw_board(canvas, piece_animations, selected_square)
        self._draw_ui(canvas, board_w)
        return canvas

    def _get_display_coords(self, r, c):
        """Returns board coordinates rotated for the black player if applicable."""
        if self.player_color == 'black':
            return 7 - r, 7 - c
        return r, c

    def _draw_board(self, canvas, piece_animations, selected_square):
        """Draws the grid, valid move indicators, and animated pieces onto the canvas."""
        board_matrix = self.facade.get_board_data()
        current_time = int(time.time() * 1000)
        cell_size = self.facade.mapper.cell_size
        piece_size = int(cell_size * constants.PIECE_SIZE_MULTIPLIER)

        if selected_square:
            for r, c in self.facade.get_valid_moves(*selected_square):
                dr, dc = self._get_display_coords(r, c)
                cx, cy = self.facade.mapper.grid_to_pixel_center(dr, dc)
                cv2.circle(canvas, (cx, cy), cell_size // constants.VALID_MOVE_RADIUS_DIV,
                           constants.COLOR_MOVE_VALID, -1)

        for r in range(constants.GRID_SIZE):
            for c in range(constants.GRID_SIZE):
                p_code = board_matrix[r][c]
                if p_code and p_code != constants.EMPTY_CELL and (anim := piece_animations.get(p_code)):
                    dr, dc = self._get_display_coords(r, c)

                    anim.set_state(getattr(self.facade._runner.status, 'piece_states', {}).get((r, c), "idle"))
                    if (frame := anim.get_current_frame(current_time)) and hasattr(frame, 'img'):
                        resized = cv2.resize(frame.img, (piece_size, piece_size))
                        cx, cy = self.facade.mapper.grid_to_pixel_center(dr, dc)
                        y1, x1 = cy - piece_size // 2, cx - piece_size // 2

                        if resized.shape[2] == 4:
                            alpha = resized[:, :, 3] / 255.0
                            for i in range(3):
                                canvas[y1:y1 + piece_size, x1:x1 + piece_size, i] = \
                                    alpha * resized[:, :, i] + (1 - alpha) * canvas[y1:y1 + piece_size,
                                                                             x1:x1 + piece_size, i]
                        else:
                            canvas[y1:y1 + piece_size, x1:x1 + piece_size] = resized

    def _draw_ui(self, canvas, board_w):
        """Draws sidebar metadata, scores, and correctly column-mapped history for each player."""
        status = self.facade._runner.status
        cv2.rectangle(canvas, (board_w, 0), (canvas.shape[1], canvas.shape[0]), constants.COLOR_SIDEBAR_BG, -1)

        turn_text = f"My Color: {self.player_color.capitalize()}"
        cv2.putText(canvas, turn_text, (board_w + constants.SIDEBAR_TEXT_X, constants.STATUS_Y), constants.FONT,
                    constants.FONT_SCALE_LARGE, constants.COLOR_TEXT_CYAN, constants.THICKNESS_MEDIUM)

        cv2.putText(canvas, "SCORES", (board_w + constants.SIDEBAR_TEXT_X, constants.SCORES_Y), constants.FONT,
                    constants.FONT_SCALE_LARGE, constants.COLOR_TEXT_YELLOW, constants.THICKNESS_MEDIUM)
        cv2.putText(canvas, f"White: {status.scores.get(constants.PLAYER_WHITE, 0)}",
                    (board_w + constants.SIDEBAR_TEXT_X, constants.SCORE_VAL_Y), constants.FONT,
                    constants.FONT_SCALE_MEDIUM, constants.COLOR_TEXT_WHITE, constants.THICKNESS_THIN)
        cv2.putText(canvas, f"Black: {status.scores.get(constants.PLAYER_BLACK, 0)}",
                    (board_w + constants.SIDEBAR_TEXT_X, constants.SCORE_VAL_Y + constants.SCORE_OFFSET_Y),
                    constants.FONT, constants.FONT_SCALE_MEDIUM, constants.COLOR_TEXT_WHITE, constants.THICKNESS_THIN)

        cv2.putText(canvas, "HISTORY", (board_w + constants.SIDEBAR_TEXT_X, constants.HISTORY_Y), constants.FONT,
                    constants.FONT_SCALE_LARGE, constants.COLOR_TEXT_YELLOW, constants.THICKNESS_MEDIUM)

        col_map = {constants.PLAYER_WHITE: board_w + constants.HISTORY_COL_WHITE,
                   constants.PLAYER_BLACK: board_w + constants.HISTORY_COL_BLACK}

        for pid in [constants.PLAYER_WHITE, constants.PLAYER_BLACK]:
            cv2.putText(canvas, "White" if pid == constants.PLAYER_WHITE else "Black", (col_map[pid], constants.NAME_Y),
                        constants.FONT, constants.FONT_SCALE_SMALL, constants.COLOR_TEXT_GRAY, constants.THICKNESS_THIN)
            y = constants.MOVE_START_Y
            for move in status.command_history.get(pid, []):
                if y < constants.HISTORY_MAX_Y:
                    cv2.putText(canvas, move, (col_map[pid], y), constants.FONT, constants.FONT_SCALE_TINY,
                                constants.COLOR_HISTORY_TEXT, constants.THICKNESS_THIN)
                    y += constants.HISTORY_TEXT_OFFSET_Y

        if status.game_over:
            overlay = canvas.copy()
            cv2.rectangle(overlay, (0, 0), (canvas.shape[1], canvas.shape[0]), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, canvas, 0.4, 0, canvas)
            cv2.putText(canvas, "GAME OVER", (board_w // 2 - constants.GAME_OVER_TITLE_X,
                                              canvas.shape[0] // 2 - constants.GAME_OVER_TITLE_Y), constants.FONT,
                        constants.FONT_SCALE_HEADER, constants.COLOR_WINNER_RED, constants.THICKNESS_BOLD)
            cv2.putText(canvas, f"{status.winner} Wins!",
                        (board_w // 2 - (constants.GAME_OVER_TITLE_X - constants.GAME_OVER_TEXT_X_OFFSET),
                         canvas.shape[0] // 2 + constants.GAME_OVER_TEXT_Y_OFFSET), constants.FONT,
                        constants.FONT_SCALE_TITLE, constants.COLOR_TEXT_WHITE, constants.THICKNESS_MEDIUM)
            cv2.putText(canvas, "Press Ctrl+N for New Game", (board_w // 2 - (constants.GAME_OVER_TITLE_X + 30),
                                                              canvas.shape[0] // 2 + constants.NEW_GAME_MSG_Y),
                        constants.FONT, constants.FONT_SCALE_MEDIUM, constants.COLOR_HISTORY_TEXT,
                        constants.THICKNESS_THIN)