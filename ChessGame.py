from BoardRepresentation import BoardRepresentation


class ChessGame:
    CELL_SIZE = 100
    VALID_COLORS = {"w", "b"}
    VALID_PIECES = {"K", "Q", "R", "B", "N", "P"}

    def __init__(self, board: BoardRepresentation):
        self._board = board
        self._selected_pos = None  # Tuple (row, col)
        self._game_clock_ms = 0

    def print_board(self) -> None:
        print(self._board.to_canonical_string())

    def wait(self, ms: int) -> None:
        self._game_clock_ms += ms

    def click(self, x: int, y: int) -> None:
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if not self._board.is_within_bounds(row, col):
            return

        is_cell_empty = self._board.is_empty(row, col)

        if self._selected_pos is None:
            if not is_cell_empty:
                self._selected_pos = (row, col)
        else:
            sel_row, sel_col = self._selected_pos

            if not is_cell_empty:
                current_token = self._board.get_token(row, col)
                selected_token = self._board.get_token(sel_row, sel_col)

                if current_token[0] == selected_token[0]:
                    self._selected_pos = (row, col)
                    return

            self._handle_move_request(from_pos=self._selected_pos, to_pos=(row, col))
            self._selected_pos = None

    def _is_path_clear(self, from_pos: tuple, to_pos: tuple) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        step_row = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        step_col = 0 if to_col == from_col else (1 if to_col > from_col else -1)

        curr_row = from_row + step_row
        curr_col = from_col + step_col

        while (curr_row, curr_col) != (to_row, to_col):
            if not self._board.is_empty(curr_row, curr_col):
                return False
            curr_row += step_row
            curr_col += step_col

        return True

    def _is_move_legal(self, piece_type: str, from_pos: tuple, to_pos: tuple) -> bool:
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
        elif piece_type == "P":
            return True

        return False

    def _handle_move_request(self, from_pos: tuple, to_pos: tuple) -> None:
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece_token = self._board.get_token(from_row, from_col)
        piece_color = piece_token[0]
        piece_type = piece_token[1]

        if not self._board.is_empty(to_row, to_col):
            target_token = self._board.get_token(to_row, to_col)
            if target_token[0] == piece_color:
                return

        if not self._is_move_legal(piece_type, from_pos, to_pos):
            return

        if piece_type in {"R", "B", "Q"}:
            if not self._is_path_clear(from_pos, to_pos):
                return

        self._board.move_piece(from_row, from_col, to_row, to_col)