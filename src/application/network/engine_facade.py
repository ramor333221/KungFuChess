import json
import websockets

from config import constants
from src.core.game_runner import GameRunner
from src.utils.UI.img import Img
from src.utils.input.BoardFactory import BoardFactory
from src.utils.input.board_mapper import BoardMapper
from src.utils.observer.observer import Subject
from src.utils.observer.score_observer import ScoreObserver


class EngineFacade(Subject):
    """
    Facade class that bridges the GUI with the game engine logic,
    handles network communication, and manages database interactions.
    """

    def __init__(self, board_path, db_manager, board_matrix=None, player_color=None, username="Player"):
        """Initializes the facade, loads board assets, and sets up game state."""
        super().__init__()
        self._runner = GameRunner()
        self.db_manager = db_manager
        self.username = username
        self.player_color = player_color
        self._board = board_matrix
        self.board_base = Img().read(board_path)
        self.mapper = BoardMapper(self.board_base.img)
        self.websocket = None
        self.opponent_username = "Unknown_Opponent"
        self._runner.status.on_game_over = self._handle_game_end

        self.attach(ScoreObserver(self.db_manager))

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    async def connect_to_server(self, uri="ws://localhost:8765", elo=1200):
        """Establishes a WebSocket connection and authenticates the player with ELO."""
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(json.dumps({
            "type": "LOGIN",
            "username": self.username,
            "elo": elo
        }))

    async def send_move(self, move_data):
        """Transmits move data to the game server."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "MOVE",
                "data": move_data
            }))

    def process_move(self, command_str):
        """Processes a local move command through the game runner, attributing history to the piece's color."""
        parts = command_str.split()
        if not parts:
            return None

        try:
            from_r = int(parts[1])
            from_c = int(parts[2])

            board_matrix = self.get_board_data()
            piece_code = board_matrix[from_r][from_c]

            if piece_code and "W" in piece_code:
                player_id = constants.PLAYER_WHITE
            elif piece_code and "B" in piece_code:
                player_id = constants.PLAYER_BLACK
            else:
                player_id = self._runner.status.current_turn
        except (IndexError, ValueError):
            player_id = self._runner.status.current_turn

        self._runner.status.add_history(player_id, command_str)

        result = self._runner.interaction_ctrl.execute_command(parts[0], parts[1:])

        if not getattr(self._runner.status, 'game_over', False):
            self.notify(constants.EVENT_MOVE_COMPLETED, {"data": command_str})

        return result

    def _handle_game_end(self):
        """Handles post-game logic and updates score statistics on game completion."""
        winner = self._runner.status.winner
        is_winner = str(winner).lower() == str(self.player_color).lower()

        winner_name = self.username if is_winner else self.opponent_username
        loser_name = self.opponent_username if is_winner else self.username

        if is_winner:
            self.notify(constants.EVENT_GAME_OVER, {
                "winner_name": winner_name,
                "loser_name": loser_name
            })

    def get_board_data(self):
        """Retrieves the current matrix representation of the game board."""
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        return [[None for _ in range(constants.BOARD_SIZE)] for _ in range(constants.BOARD_SIZE)]

    def get_valid_moves(self, row, col):
        """Calculates valid moves for a piece at the specified position."""
        return self._runner.get_possible_moves(row, col)

    def get_game_over_status(self):
        """Checks if the game has reached a terminal state."""
        return getattr(self._runner.status, 'game_over', False)

    def switch_player_turn(self):
        """Transitions the turn to the next player."""
        self._runner.status.selected_pos = None
        self._runner.status.switch_turn()

    def reset_game(self):
        """Resets the board, scores, and all temporary move states."""
        self._runner.status.game_over = False
        self._runner.status.winner = None
        self._runner.status.current_turn = constants.PLAYER_WHITE
        self._runner.status.game_clock_ms = 0
        self._runner.status.scores = {constants.PLAYER_WHITE: 0, constants.PLAYER_BLACK: 0}

        if self._runner.board:
            self._runner.board.matrix = BoardFactory.get_default_layout()

        self._runner.chronology.pending_movements.clear()
        self._runner.chronology.airborne_pieces.clear()
        self._runner.status.moved_pieces.clear()

        if hasattr(self._runner.status, 'piece_states'):
            self._runner.status.piece_states.clear()

    async def wait_for_match_and_listen(self, on_start_callback):
        """Waits for the START message from the server in the background."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                if message is None:
                    continue

                data = json.loads(message)
                msg_type = data.get('type')

                if msg_type == 'START':
                    self.player_color = data.get('color')
                    self.opponent_username = data.get('opponent', "Unknown_Opponent")
                    room_id = data.get('room')

                    await on_start_callback(room_id)
                    break
        except Exception as e:
            pass

    async def listen_for_moves(self, callback):
        """Listens continuously for remote move commands and server event notifications."""
        if not self.websocket:
            return
        try:
            async for message in self.websocket:
                if message is None:
                    continue

                data = json.loads(message)
                callback(data)

        except Exception as e:
            pass