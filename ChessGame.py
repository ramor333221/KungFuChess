class ChessGame:
    CELL_SIZE = 100
    VALID_COLORS = {"w", "b"}
    VALID_PIECES = {"K", "Q", "R", "B", "N", "P"}

    def __init__(self, board_grid):
        self.grid = board_grid
        self.height = len(board_grid)
        self.width = len(board_grid[0]) if self.height > 0 else 0

        self.selected_pos = None  # Tuple (row, col)
        self.game_clock_ms = 0

    def print_board(self):
        """Outputs the current board state in its canonical form."""
        for row in self.grid:
            print(" ".join(row))

    def wait(self, ms: int):
        """Advances the internal game clock."""
        self.game_clock_ms += ms

    def click(self, x: int, y: int):
        """Processes a pixel click event, translating coordinates to board cells."""
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if not (0 <= row < self.height and 0 <= col < self.width):
            return

        clicked_token = self.grid[row][col]
        is_empty = (clicked_token == ".")

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
            if self.grid[curr_row][curr_col] != ".":
                return False
            curr_row += step_row
            curr_col += step_col

        return True

    def _is_pawn_move_legal(self, color: str, from_pos: tuple, to_pos: tuple) -> bool:
        """Validates standard single-step pawn logic and diagonal captures."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # לבן נע למעלה (מינוס בשורות), שחור נע למטה (פלוס בשורות)
        forward_dir = -1 if color == "w" else 1

        row_diff = to_row - from_row
        col_diff = to_col - from_col
        target_token = self.grid[to_row][to_col]

        # 1. תנועה קדימה: בדיוק צעד אחד, באותה עמודה.
        # חייב להיות ריק (מונע אכילה קדימה ומונע תנועה של 2 צעדים)
        if row_diff == forward_dir and col_diff == 0:
            return target_token == "."

            # 2. אכילה באלכסון: בדיוק צעד אחד קדימה וצעד אחד הצידה.
        # חייב להיות שם כלי כלשהו (הבדיקה מול כלי ידידותי נעשית כבר ב-handle_move_request)
        if row_diff == forward_dir and abs(col_diff) == 1:
            return target_token != "."

        return False

    def _is_move_legal(self, piece_type: str, from_pos: tuple, to_pos: tuple) -> bool:
        """Validates whether a move adheres to geometric path limitations."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)

        if d_row == 0 and d_col == 0:
            return False

        if piece_type == "K":
            return d_row <= 1 and d_col <= 1
        elif piece_type == "R":
            return d_row == 0 or d_col == 0
        elif piece_type == "B":
            return d_row == d_col
        elif piece_type == "Q":
            return d_row == 0 or d_col == 0 or d_row == d_col
        elif piece_type == "N":
            return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)

        return False

    def _handle_move_request(self, from_pos: tuple, to_pos: tuple):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece_token = self.grid[from_row][from_col]
        piece_color = piece_token[0]
        piece_type = piece_token[1]

        target_token = self.grid[to_row][to_col]

        # Prevent capturing friendly pieces
        if target_token != "." and target_token[0] == piece_color:
            return

        # Core Routing for Pawn vs. Normal Pieces
        if piece_type == "P":
            if not self._is_pawn_move_legal(piece_color, from_pos, to_pos):
                return
        else:
            if not self._is_move_legal(piece_type, from_pos, to_pos):
                return
            # Path obstruction validation for sliding pieces
            if piece_type in {"R", "B", "Q"}:
                if not self._is_path_clear(from_pos, to_pos):
                    return

        # Apply spatial state mutation
        self.grid[to_row][to_col] = piece_token
        self.grid[from_row][from_col] = "."