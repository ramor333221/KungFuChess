from BoardRepresentation import BoardRepresentation


class ChessGame:
    CELL_SIZE = 100
    VALID_COLORS = {"w", "b"}
    VALID_PIECES = {"K", "Q", "R", "B", "N", "P"}

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

            self._handle_move_request(from_pos=self._selected_pos, to_pos=(row, col))
            self._selected_pos = None

    def _is_move_legal(self, piece_type: str, from_pos: tuple, to_pos: tuple) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)

        if d_row == 0 and d_col == 0:
            return False

        if piece_type == "K":  # King
            return d_row <= 1 and d_col <= 1
        elif piece_type == "R":  # Rook
            return d_row == 0 or d_col == 0
        elif piece_type == "B":  # Bishop
            return d_row == d_col
        elif piece_type == "Q":  # Queen
            return d_row == 0 or d_col == 0 or d_row == d_col
        elif piece_type == "N":  # Knight
            return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)
        elif piece_type == "P":  # Pawn
            return True

        return False

    def _handle_move_request(self, from_pos: tuple, to_pos: tuple) -> None:
        from_row, from_col = from_pos
        piece_token = self._board.get_token(from_row, from_col)
        piece_type = piece_token[1]

        if self._is_move_legal(piece_type, from_pos, to_pos):
            self._board.move_piece(from_row, from_col, to_pos[0], to_pos[1])