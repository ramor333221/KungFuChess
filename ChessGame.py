import sys


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
        self.pending_movements = []

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
        # תמיד נעדכן תנועות לפני עיבוד לחיצה כדי לשחרר את הנעילה אם הזמן עבר
        self._implement_movement()

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

        forward_dir = -1 if color == "w" else 1

        row_diff = to_row - from_row
        col_diff = to_col - from_col
        target_token = self.grid[to_row][to_col]

        if row_diff == forward_dir and col_diff == 0:
            return target_token == "."

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

        # אם משבצת המקור כבר התרוקנה (למשל כלי כבר בדרך), נתעלם
        if piece_token == ".":
            return

        piece_color = piece_token[0]
        piece_type = piece_token[1]
        target_token = self.grid[to_row][to_col]

        # חסימה גלובלית: מניעת פקודות חדשות אם יש כלי בדרך
        if len(self.pending_movements) > 0:
            return

        if target_token != "." and target_token[0] == piece_color:
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

        arrival = self.game_clock_ms + 1000
        self.pending_movements.append({
            "from": from_pos,
            "to": to_pos,
            "piece": piece_token,
            "arrival_time": arrival
        })

        # מוחקים מיד את הכלי ממשבצת המקור כדי שלא יהיה ניתן להזיז אותו שוב בטעות בזמן הטיסה
        self.grid[from_row][from_col] = "."

    def _implement_movement(self):
        still_traveling = []

        for movement in self.pending_movements:
            # הכלים מגיעים רשמית ליעד בזמן >= (למשל אחרי wait 1000)
            if self.game_clock_ms >= movement["arrival_time"]:
                to_row, to_col = movement["to"]
                self.grid[to_row][to_col] = movement["piece"]
            else:
                still_traveling.append(movement)

        self.pending_movements = still_traveling


class CommandParser:
    @staticmethod
    def parse_initial_input():
        lines = [line.strip() for line in sys.stdin]
        board_rows = []
        command_lines = []

        is_board_section = False
        is_command_section = False

        for line in lines:
            if not line:
                continue
            if line.startswith("Board:"):
                is_board_section = True
                continue
            if line.startswith("Commands:"):
                is_board_section = False
                is_command_section = True
                continue

            if is_board_section:
                tokens = line.split()
                if tokens:
                    board_rows.append(tokens)
            elif is_command_section:
                command_lines.append(line)

        return board_rows, command_lines

    @staticmethod
    def validate_board(board_rows) -> bool:
        if not board_rows:
            return False
        expected_width = len(board_rows[0])
        for row in board_rows:
            if len(row) != expected_width:
                print("ERROR ROW_WIDTH_MISMATCH")
                return False
            for token in row:
                if token == ".":
                    continue
                if len(token) != 2 or token[0] not in ChessGame.VALID_COLORS or token[1] not in ChessGame.VALID_PIECES:
                    print("ERROR UNKNOWN_TOKEN")
                    return False
        return True


def main():
    board_rows, command_lines = CommandParser.parse_initial_input()
    if not CommandParser.validate_board(board_rows):
        return

    game = ChessGame(board_rows)

    for command in command_lines:
        parts = command.split()
        if not parts:
            continue

        cmd_type = parts[0]

        if cmd_type == "click" and len(parts) == 3:
            try:
                x, y = int(parts[1]), int(parts[2])
                game.click(x, y)
            except ValueError:
                continue
        elif cmd_type == "wait" and len(parts) == 2:
            try:
                ms = int(parts[1])
                game.wait(ms)
            except ValueError:
                continue
        elif command == "print board":
            game.print_board()


if __name__ == "__main__":
    main()