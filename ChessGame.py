from BoardRepresentation import BoardRepresentation


class ChessGame:
    CELL_SIZE = 100

    def __init__(self, board: BoardRepresentation):
        self._board = board
        self._selected_pos = None
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

            self._board.move_piece(sel_row, sel_col, row, col)
            self._selected_pos = None