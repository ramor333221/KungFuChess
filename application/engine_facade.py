from core.config import constants
from core.game_runner import GameRunner
from utils.BoardFactory import BoardFactory
from utils.board_mapper import BoardMapper
from utils.img import Img


class EngineFacade:
    def __init__(self, board_path, board_matrix=None):
        self._runner = GameRunner()
        self._board = board_matrix
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


    def get_game_over_status(self):
        """Returns True if the game is over, False otherwise."""
        if hasattr(self._runner, 'status'):
            return self._runner.status.game_over
        return False

    def reset_game(self):
        # 1. Reset Status and Turn
        self._runner.status.game_over = False
        self._runner.status.winner = None
        self._runner.status.current_turn = constants.PLAYER_WHITE
        self._runner.status.game_clock_ms = 0

        # 2. Reset Scores to 0
        self._runner.status.scores = {
            constants.PLAYER_WHITE: 0,
            constants.PLAYER_BLACK: 0
        }

        # 3. Wipe and Repopulate the Board Matrix
        board_obj = self._runner.board
        if board_obj:
            initial_layout = BoardFactory.get_default_layout()
            for r in range(constants.GRID_SIZE):
                for c in range(constants.GRID_SIZE):
                    board_obj.matrix[r][c] = initial_layout[r][c]

        # 4. Clear move queues and piece states
        self._runner.chronology.pending_movements.clear()
        self._runner.chronology.airborne_pieces.clear()
        self._runner.status.moved_pieces.clear()

        if hasattr(self._runner.status, 'piece_states'):
            self._runner.status.piece_states.clear()

        print("Game and scores reset successfully.")