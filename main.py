import constants


class ChessGame:
    CELL_SIZE = constants.CELL_SIZE
    EMPTY_CELL = constants.EMPTY_CELL

    def __init__(self, board_grid):
        self.grid = board_grid
        self.height = len(board_grid)
        self.width = len(board_grid[0]) if self.height > 0 else 0
        self.selected_pos = None
        self.game_clock_ms = 0
        self.pending_movements = []
        self.airborne_pieces = {}  # מיפוי: {(row, col): {"piece": str, "arrival_time": int}}
        self.moved_pieces = set()  # מעקב אחרי כלים שכבר זזו
        self.game_over = False

    def click(self, x: int, y: int):
        if self.game_over: return
        self._implement_movement()

        col, row = x // self.CELL_SIZE, y // self.CELL_SIZE
        if not (0 <= row < self.height and 0 <= col < self.width): return

        clicked_token = self.grid[row][col]

        if self.selected_pos is None:
            if clicked_token != self.EMPTY_CELL:
                self.selected_pos = (row, col)
        else:
            if (row, col) == self.selected_pos:
                self.selected_pos = None
            else:
                self._handle_move_request(self.selected_pos, (row, col))
                self.selected_pos = None

    def jump(self, *args):
        """
        מפעיל מצב קפיצה לכלי.
        אם המשחק כבר הסתיים (למשל המלך נאכל), הפקודה נכשלת בשקט.
        """
        if self.game_over: return  # טסט 3: המלך כבר נאכל, אי אפשר לקפוץ!

        if len(args) == 1:
            if isinstance(args[0], tuple) or isinstance(args[0], list):
                raw_pos = args[0]
            else:
                return
        elif len(args) == 2:
            raw_pos = (args[0], args[1])
        else:
            return

        # תרגום פיקסלים לאינדקסים בדיוק כמו ב-click
        col = raw_pos[0] // self.CELL_SIZE
        row = raw_pos[1] // self.CELL_SIZE
        pos = (row, col)

        if not (0 <= pos[0] < self.height and 0 <= pos[1] < self.width): return

        piece = self.grid[pos[0]][pos[1]]
        if piece == self.EMPTY_CELL: return

        # שמירת הכלי באוויר והסרתו מהלוח
        self.airborne_pieces[pos] = {
            "piece": piece,
            "arrival_time": self.game_clock_ms + 1000
        }
        self.grid[pos[0]][pos[1]] = self.EMPTY_CELL

    def _implement_movement(self):
        # 1. שלב ראשון: עיבוד תנועות רגילות שמגיעות ליעדן
        still_traveling = []
        for m in self.pending_movements:
            if self.game_clock_ms >= m["arrival_time"]:
                r, c = m["to"]
                piece = m["piece"]

                # האם יש כלי באוויר במשבצת הזו כרגע?
                if (r, c) in self.airborne_pieces:
                    airborne_data = self.airborne_pieces[(r, c)]
                    if piece[0] != airborne_data["piece"][0]:
                        # אויב מגיע: הכלי שבאוויר לוכד אותו בשמיים, התנועה מתבטלת בשקט
                        continue
                    else:
                        # חבר מגיע: התנועה מבוטלת והכלי הידידותי חוזר למקומו המקורי
                        self.grid[m["from"][0]][m["from"][1]] = piece
                        continue

                # תנועה רגילה ללא הפרעה
                self.moved_pieces.add(m["from"])
                if piece[1] == "P" and self.height >= 8:
                    last_row = 0 if piece[0] == "w" else (self.height - 1)
                    if r == last_row:
                        piece = piece[0] + "Q"

                if self.grid[r][c] != self.EMPTY_CELL and self.grid[r][c][1] == "K":
                    self.game_over = True

                self.grid[r][c] = piece
            else:
                still_traveling.append(m)
        self.pending_movements = still_traveling

        # 2. שלב שני: הכלים שבאוויר נוחתים חזרה ללוח
        for pos, data in list(self.airborne_pieces.items()):
            if self.game_clock_ms >= data["arrival_time"]:
                r, c = pos
                if self.grid[r][c] == self.EMPTY_CELL:
                    self.grid[r][c] = data["piece"]
                del self.airborne_pieces[pos]

    def _handle_move_request(self, from_pos, to_pos):
        if len(self.pending_movements) > 0: return
        piece = self.grid[from_pos[0]][from_pos[1]]
        if piece == self.EMPTY_CELL: return

        color, p_type = piece[0], piece[1]
        is_legal = False
        if p_type == "P":
            is_legal = self._is_pawn_move_legal(color, from_pos, to_pos)
        else:
            is_legal = self._is_move_legal(p_type, from_pos, to_pos)
            if is_legal and p_type in {"R", "B", "Q"}:
                is_legal = self._is_path_clear(from_pos, to_pos)

        if not is_legal: return

        self.pending_movements.append({
            "from": from_pos, "to": to_pos, "piece": piece,
            "arrival_time": self.game_clock_ms + constants.MOVEMENT_DURATION_MS
        })
        self.grid[from_pos[0]][from_pos[1]] = self.EMPTY_CELL

    def _is_move_legal(self, piece_type, from_pos, to_pos):
        r1, c1 = from_pos
        r2, c2 = to_pos
        d_row, d_col = abs(r2 - r1), abs(c2 - c1)
        if d_row == 0 and d_col == 0: return False
        if piece_type == "K": return d_row <= 1 and d_col <= 1
        if piece_type == "R": return d_row == 0 or d_col == 0
        if piece_type == "B": return d_row == d_col
        if piece_type == "Q": return d_row == 0 or d_col == 0 or d_row == d_col
        if piece_type == "N": return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)
        return False

    def _is_pawn_move_legal(self, color, from_pos, to_pos):
        r1, c1 = from_pos
        r2, c2 = to_pos
        fwd = -1 if color == "w" else 1
        dr, dc = r2 - r1, c2 - c1
        if dr == fwd and dc == 0:
            return self.grid[r2][c2] == self.EMPTY_CELL
        if dr == 2 * fwd and dc == 0:
            if from_pos not in self.moved_pieces:
                return self.grid[r1 + fwd][c1] == self.EMPTY_CELL and self.grid[r2][c2] == self.EMPTY_CELL
        if dr == fwd and abs(dc) == 1:
            return self.grid[r2][c2] != self.EMPTY_CELL and self.grid[r2][c2][0] != color
        return False

    def _is_path_clear(self, from_pos, to_pos):
        r, c = from_pos
        dr = (to_pos[0] - r) // max(1, abs(to_pos[0] - r)) if r != to_pos[0] else 0
        dc = (to_pos[1] - c) // max(1, abs(to_pos[1] - c)) if c != to_pos[1] else 0
        r, c = r + dr, c + dc
        while (r, c) != to_pos:
            if self.grid[r][c] != self.EMPTY_CELL: return False
            r, c = r + dr, c + dc
        return True

    def wait(self, ms):
        self.game_clock_ms += ms
        self._implement_movement()

    def print_board(self):
        self._implement_movement()
        for row in self.grid:
            print(" ".join(row))