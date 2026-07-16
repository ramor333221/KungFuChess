# application/board_factory.py
class BoardFactory:
    @staticmethod
    def get_default_layout():
        # Initialize empty 8x8 grid with None (or your constants.EMPTY_CELL)
        board = [[None for _ in range(8)] for _ in range(8)]

        # Correct format: [Color][Piece]
        # W = White, B = Black | R, N, B, Q, K, P
        white_back_row = ['WR', 'WN', 'WB', 'WQ', 'WK', 'WB', 'WN', 'WR']
        black_back_row = ['BR', 'BN', 'BB', 'BQ', 'BK', 'BB', 'BN', 'BR']

        for col in range(8):
            board[0][col] = black_back_row[col]  # Black back row
            board[1][col] = 'BP'  # Black pawns
            board[6][col] = 'WP'  # White pawns
            board[7][col] = white_back_row[col]  # White back row

        return board