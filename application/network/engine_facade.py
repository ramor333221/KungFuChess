import asyncio
import websockets
import json

from config import constants
from core.game_runner import GameRunner
from utils.UI.img import Img
from utils.input.BoardFactory import BoardFactory
from utils.input.board_mapper import BoardMapper


class EngineFacade:
    """
    Facade class that bridges the GUI with the game engine logic
    and handles network communication via WebSockets.
    """

    def __init__(self, board_path, board_matrix=None, player_color=None):
        """Initializes the facade, loads the board, and sets the player color."""
        self._runner = GameRunner()
        self.player_color = player_color
        self._board = board_matrix
        self.board_base = Img().read(board_path)
        self.mapper = BoardMapper(self.board_base.img)
        self.websocket = None

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    # --- Network Communication ---

    async def connect_to_server(self, uri="ws://localhost:8765"):
        """Establishes a WebSocket connection and logs the player in."""
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(json.dumps({
            "type": "LOGIN",
            "player": self.player_color
        }))

    async def send_move(self, move_data):
        """Sends a move command to the game server via WebSocket."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "MOVE",
                "data": move_data
            }))

    # --- Game Logic & Status ---

    def process_move(self, command_str):
        """Executes a move command and updates the game history."""
        parts = command_str.split()
        if not parts:
            return None

        player_id = self._runner.status.current_turn
        command = parts[0]
        args = parts[1:]
        self._runner.status.add_history(player_id, command_str)
        return self._runner.interaction_ctrl.execute_command(command, args)

    def get_board_data(self):
        """Retrieves the current matrix representation of the board."""
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        return [[None for _ in range(8)] for _ in range(8)]

    def get_valid_moves(self, row, col):
        """Returns all valid moves for the piece at the given position."""
        return self._runner.get_possible_moves(row, col)

    def get_game_over_status(self):
        """Checks if the game has reached an end state."""
        return getattr(self._runner.status, 'game_over', False)

    def switch_player_turn(self):
        """Switches the current turn and clears the selected position."""
        self._runner.status.selected_pos = None
        self._runner.status.switch_turn()
        print(f"EngineFacade: Turn switched to {self._runner.status.current_turn}")

    def reset_game(self):
        """Resets the game board, scores, and all temporary move states."""
        self._runner.status.game_over = False
        self._runner.status.winner = None
        self._runner.status.current_turn = constants.PLAYER_WHITE
        self._runner.status.game_clock_ms = 0
        self._runner.status.scores = {constants.PLAYER_WHITE: 0, constants.PLAYER_BLACK: 0}

        if self._runner.board:
            initial_layout = BoardFactory.get_default_layout()
            self._runner.board.matrix = initial_layout

        self._runner.chronology.pending_movements.clear()
        self._runner.chronology.airborne_pieces.clear()
        self._runner.status.moved_pieces.clear()

        if hasattr(self._runner.status, 'piece_states'):
            self._runner.status.piece_states.clear()

        print("Game and scores reset successfully.")

    async def listen_for_moves(self, callback):
        """Listen for moves from the server and trigger the callback."""
        if not self.websocket:
            return
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if data.get('type') == 'MOVE':
                    callback(data['data'])
                elif data.get('type') == 'START':
                    print(f"Log: Game started, Room: {data.get('room')}")
        except Exception as e:
            print(f"Log: Connection error {e}")