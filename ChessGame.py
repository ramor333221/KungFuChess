# ChessGame.py
import sys
import constants


class ChessGame:
    CELL_SIZE = constants.CELL_SIZE
    EMPTY_CELL = constants.EMPTY_CELL

    def __init__(self, board_grid):
        self.grid = board_grid
        self.height = len(board_grid)
        self.width = len(board_grid[0]) if self.height > 0 else 0

        self.selected_pos = None  # Tuple (row, col)
        self.game_clock_ms = 0
        self.pending_movements = []

        self.game_over = False

    def print_board(self):
        """Outputs the current board state in its canonical form."""
        self._implement_movement()
        for row in self.grid:
            print(" ".join(row))

    def wait(self, ms: int):
        """Advances the internal game clock."""
        self.game_clock_ms += ms
        self._implement_movement()

    def click(self, x: int, y: int):
        """Processes a pixel click event, translating coordinates to board cells."""

        if self.game_over:
            return

        self._implement_movement()

        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if not (0 <= row < self.height and 0 <= col < self.width):
            return

        clicked_token = self.grid[row][col]
        is_empty = (clicked_token == self.EMPTY_CELL)

        if self.selected_pos is None:
            if not is_empty:
                self.selected_pos = (row, col)
        else:
            sel_row, sel_col = self.selected_pos
            selected_token = self.grid[sel_row][sel_col]

            if not is_empty and clicked_token[0] == selected_token[0]:
                self.selected_pos = (row, col)
            else:
                self._handle_move_request(from_pos=self.selected_pos, to_pos=(row, col))
                self.selected_pos = None

    def _is_path_clear(self, from_pos: tuple, to_pos: tuple) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        step_row = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        step_col = 0 if to_col == from_col else (1 if to_col > from_col else -1)

        curr_row = from_row + step_row
        curr_col = from_col + step_col

        while (curr_row, curr_col) != (to_row, to_col):
            if self.grid[curr_row][curr_col] != self.EMPTY_CELL:
                return False
            curr_row += step_row
            curr_col += step_col

        return True

    def _is_pawn_move_legal(self, color: str, from_pos: tuple, to_pos: tuple) -> bool:
        """Validates standard single-step pawn logic and diagonal captures."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        forward_dir = -1 if color == "w" else 1

        row_diff = to_row - from_row
        col_diff = to_col - from_col
        target_token = self.grid[to_row][to_col]

        if row_diff == forward_dir and col_diff == 0:
            return target_token == self.EMPTY_CELL

        if row_diff == forward_dir and abs(col_diff) == 1:
            return target_token != self.EMPTY_CELL

        return False

    def _is_pawn_move_legal(self, color: str, from_pos: tuple, to_pos: tuple) -> bool:
        """Validates standard single-step, initial double-step pawn logic, and diagonal captures."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        forward_dir = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1  # התאמה לשורת המקור (לפי גודל לוח סטנדרטי)

        row_diff = to_row - from_row
        col_diff = to_col - from_col
        target_token = self.grid[to_row][to_col]

        # צעד אחד קדימה (רגיל)
        if row_diff == forward_dir and col_diff == 0:
            return target_token == self.EMPTY_CELL

        # צעד כפול משורת ההתחלה (חדש!)
        if from_row == start_row and row_diff == 2 * forward_dir and col_diff == 0:
            # בודקים שגם משבצת האמצע וגם משבצת היעד ריקות
            mid_row = from_row + forward_dir
            return (self.grid[mid_row][from_col] == self.EMPTY_CELL and
                    target_token == self.EMPTY_CELL)

        # אכילה באלכסון
        if row_diff == forward_dir and abs(col_diff) == 1:
            return target_token != self.EMPTY_CELL

        return False

    def _handle_move_request(self, from_pos: tuple, to_pos: tuple):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece_token = self.grid[from_row][from_col]

        if piece_token == self.EMPTY_CELL:
            return

        piece_color = piece_token[0]
        piece_type = piece_token[1]
        target_token = self.grid[to_row][to_col]

        # חסימה גלובלית בזמן תנועה
        if len(self.pending_movements) > 0:
            return

        if target_token != self.EMPTY_CELL and target_token[0] == piece_color:
            return

        if piece_type == "P":
            if not self._is_pawn_move_legal(piece_color, from_pos, to_pos):
                return
        else:
            if not self._is_move_legal(piece_type, from_pos, to_pos):
                return

            if piece_type in {"R", "B", "Q"}:
                if not self._is_path_clear(from_pos, to_pos):
                    return

        arrival = self.game_clock_ms + constants.MOVEMENT_DURATION_MS
        self.pending_movements.append({
            "from": from_pos,
            "to": to_pos,
            "piece": piece_token,
            "arrival_time": arrival
        })

        self.grid[from_row][from_col] = self.EMPTY_CELL

    def _implement_movement(self):
        """מקדמת ומחילה את התנועות שהגיעו ליעדן בשעון הנוכחי."""
        still_traveling = []

        for movement in self.pending_movements:
            if self.game_clock_ms >= movement["arrival_time"]:
                to_row, to_col = movement["to"]
                piece = movement["piece"]  # למשל 'wP'

                # 1. בדיקת Game Over (מהשלב הקודם)
                target_piece = self.grid[to_row][to_col]
                if len(target_piece) == 2 and target_piece[1] == "K":
                    self.game_over = True

                # 2. בדיקת הכתרה (חדש!)
                piece_color = piece[0]
                piece_type = piece[1]
                last_row = 0 if piece_color == "w" else (self.height - 1)

                if piece_type == "P" and to_row == last_row:
                    piece = f"{piece_color}Q"  # החייל מוכתר למלכה!

                # החלת התנועה על הלוח
                self.grid[to_row][to_col] = piece
            else:
                still_traveling.append(movement)

        self.pending_movements = still_traveling