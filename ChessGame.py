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
        self.game_over = False
        self.moved_pawns = set()

    def click(self, x: int, y: int):
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
                self._handle_move_request(self.selected_pos, (row, col))
                self.selected_pos = None

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

        # 1. צעד רגיל - חוקי תמיד אם המשבצת ריקה
        if dr == fwd and dc == 0:
            return self.grid[r2][c2] == self.EMPTY_CELL

        # 2. צעד כפול - חוקי רק אם:
        #    א. מדובר בצעד של 2 משבצות
        #    ב. המשבצות בדרך וביעד ריקות
        #    ג. החייל לא זז עדיין (הוסף כאן את בדיקת הדגל שלך)
        if dr == 2 * fwd and dc == 0:
            if from_pos not in self.moved_pawns:  # דגל המניעה
                return self.grid[r1 + fwd][c1] == self.EMPTY_CELL and self.grid[r2][c2] == self.EMPTY_CELL

        # 3. אכילה
        if dr == fwd and abs(dc) == 1:
            return self.grid[r2][c2] != self.EMPTY_CELL and self.grid[r2][c2][0] != color

    def _handle_move_request(self, from_pos, to_pos):
        if len(self.pending_movements) > 0: return

        piece = self.grid[from_pos[0]][from_pos[1]]
        if piece == self.EMPTY_CELL: return

        color, p_type = piece[0], piece[1]

        # הגדרת משתנה בצורה בטוחה
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

    def _implement_movement(self):
        still_traveling = []
        for m in self.pending_movements:
            if self.game_clock_ms >= m["arrival_time"]:
                r, c = m["to"]
                piece = m["piece"]
                self.moved_pawns.add((r, c))

                # הכתרה
                last_row = 0 if piece[0] == "w" else (self.height - 1)
                if piece[1] == "P" and r == last_row:
                    piece = piece[0] + "Q"

                # Game Over
                if self.grid[r][c] != self.EMPTY_CELL and self.grid[r][c][1] == "K":
                    self.game_over = True

                self.grid[r][c] = piece
            else:
                still_traveling.append(m)
        self.pending_movements = still_traveling


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
        for row in self.grid: print(" ".join(row))