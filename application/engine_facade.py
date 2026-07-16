# application/engine_facade.py
from core.game_runner import GameRunner
from utils.BoardFactory import BoardFactory
from utils.board_mapper import BoardMapper
# Import your new factory


class EngineFacade:
    def __init__(self, board_matrix=None):
        self._runner = GameRunner()
        self.mapper = BoardMapper()

        # 1. Resolve the matrix using the factory if none provided
        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        # 2. Run the game initialization with the matrix
        self._runner.run_game(board_matrix, [])

    def process_move(self, command_str):
        parts = command_str.split()  # ["click", "row", "col"]
        command = parts[0]  # "click"
        args = parts[1:]  # ["row", "col"]

        return self._runner.interaction_ctrl.execute_command(command, args)

    def get_board_data(self):
        """Returns the board matrix for the GUI to render."""
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        # Return an empty 8x8 matrix if board not initialized
        return [[None for _ in range(8)] for _ in range(8)]

    def handle_gui_click(self, x, y):
        row, col = self.mapper.pixel_to_grid(x, y)
        self._runner.interaction_ctrl.execute_command("click", [row, col])