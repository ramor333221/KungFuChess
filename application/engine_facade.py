from core.game_runner import GameRunner
from utils.BoardFactory import BoardFactory
from utils.board_mapper import BoardMapper
from utils.img import Img


class EngineFacade:
    def __init__(self, board_path, board_matrix=None):
        self._runner = GameRunner()

        # 1. Load the board image
        self.board_base = Img().read(board_path)

        # 2. Initialize the mapper using the image
        self.mapper = BoardMapper(self.board_base.img)

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    def process_move(self, command_str):
        parts = command_str.split()
        if not parts:
            return None

        command = parts[0]
        args = parts[1:]
        print(f"Executing: {command} with args: {args}")  # Debugging
        return self._runner.interaction_ctrl.execute_command(command, args)

    def get_board_data(self):
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        return [[None for _ in range(8)] for _ in range(8)]

    def get_valid_moves(self, row, col):
        """Delegates directly to the Runner."""
        return self._runner.get_possible_moves(row, col)

    # application/engine_facade.py

    def get_game_over_status(self):
        """Returns True if the game is over, False otherwise."""
        if hasattr(self._runner, 'status'):
            return self._runner.status.game_over
        return False