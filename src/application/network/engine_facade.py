from config import constants
from src.core.game_runner import GameRunner
from src.utils.UI.img import Img
from src.utils.input.BoardFactory import BoardFactory
from src.utils.input.board_mapper import BoardMapper
from src.utils.observer.achievement_observer import AchievementObserver
from src.utils.observer.move_observer import MoveLoggerObserver
from src.utils.observer.observer import Subject
from src.utils.observer.score_observer import ScoreObserver
from src.utils.observer.sound_observer import SoundObserver


class EngineFacade(Subject):
    """Facade class bridging the GUI with the game engine logic using the Observer pattern."""

    def __init__(self, board_path, db_manager, board_matrix=None, player_color=None, username="Player", network_client=None):
        super().__init__()
        self._runner = GameRunner()
        self.db_manager = db_manager
        self.username = username
        self.network_client = network_client
        self.player_color = player_color
        self._board = board_matrix
        self.board_base = Img().read(board_path)
        self.mapper = BoardMapper(self.board_base.img)
        self._runner.status.on_game_over = self._handle_game_end

        self.attach(ScoreObserver(self.db_manager))
        self.attach(MoveLoggerObserver())
        self.attach(AchievementObserver())
        self.attach(SoundObserver())

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    @property
    def websocket(self):
        """Proxy property for network client websocket."""
        return self.network_client.websocket if self.network_client else None

    @websocket.setter
    def websocket(self, value):
        """Proxy setter for network client websocket."""
        if self.network_client:
            self.network_client.websocket = value

    @property
    def opponent_username(self):
        """Proxy property for opponent username."""
        return self.network_client.opponent_username if self.network_client else constants.UNKNOWN_OPPONENT

    @opponent_username.setter
    def opponent_username(self, value):
        """Proxy setter for opponent username."""
        if self.network_client:
            self.network_client.opponent_username = value

    @property
    def room_name(self):
        """Proxy property for room name."""
        return self.network_client.room_name if self.network_client else None

    @room_name.setter
    def room_name(self, value):
        """Proxy setter for room name."""
        if self.network_client:
            self.network_client.room_name = value

    @property
    def broker(self):
        """Proxy property for message broker."""
        return self.network_client.broker if self.network_client else None

    @property
    def on_server_message(self):
        """Proxy property for server message handler."""
        return self.network_client.on_server_message if self.network_client else None

    @on_server_message.setter
    def on_server_message(self, value):
        """Proxy setter for server message handler."""
        if self.network_client:
            self.network_client.on_server_message = value

    @property
    def on_opponent_disconnect(self):
        """Proxy property for opponent disconnect handler."""
        return self.network_client.on_opponent_disconnect if self.network_client else None

    @on_opponent_disconnect.setter
    def on_opponent_disconnect(self, value):
        """Proxy setter for opponent disconnect handler."""
        if self.network_client:
            self.network_client.on_opponent_disconnect = value

    @property
    def player_color(self):
        """Proxy property for player color."""
        return self.network_client.player_color if self.network_client else self._player_color

    @player_color.setter
    def player_color(self, value):
        """Proxy setter for player color."""
        if self.network_client:
            self.network_client.player_color = value
        self._player_color = value

    async def connect_to_server(self, uri=constants.DEFAULT_WS_URI, elo=constants.DEFAULT_ELO):
        """Connect to the server via the network client."""
        if self.network_client:
            await self.network_client.connect_to_server(uri, elo)

    async def send_move(self, move_data):
        """Send a move via the network client."""
        if self.network_client:
            await self.network_client.send_move(move_data)

    def process_move(self, command_str):
        """Process a game move command and notify observers."""
        parts = command_str.split()
        if not parts:
            return None

        try:
            from_r = int(parts[1])
            from_c = int(parts[2])
            board_matrix = self.get_board_data()
            piece_code = board_matrix[from_r][from_c]

            if piece_code and constants.PIECE_WHITE_INDICATOR in piece_code:
                player_id = constants.PLAYER_WHITE
            elif piece_code and constants.PIECE_BLACK_INDICATOR in piece_code:
                player_id = constants.PLAYER_BLACK
            else:
                player_id = self._runner.status.current_turn
        except (IndexError, ValueError):
            player_id = self._runner.status.current_turn

        self._runner.status.add_history(player_id, command_str)
        result = self._runner.interaction_ctrl.execute_command(parts[0], parts[1:])

        if not getattr(self._runner.status, constants.ATTR_GAME_OVER, False):
            self.notify(constants.EVENT_MOVE_COMPLETED, {"data": command_str})

        return result

    def _handle_game_end(self):
        """Handle game over event and notify observers of winner and loser."""
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
        """Retrieve the current board matrix data."""
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        return [[None for _ in range(constants.BOARD_SIZE)] for _ in range(constants.BOARD_SIZE)]

    def get_valid_moves(self, row, col):
        """Get valid move coordinates for a piece at given row and column."""
        return self._runner.get_possible_moves(row, col)

    def get_game_over_status(self):
        """Return whether the game is over."""
        return getattr(self._runner.status, constants.ATTR_GAME_OVER, False)

    def switch_player_turn(self):
        """Switch the active player turn."""
        self._runner.status.selected_pos = None
        self._runner.status.switch_turn()

    async def initialize_broker_listeners(self):
        """Initialize broker event listeners via network client."""
        if self.network_client:
            self.network_client.on_remote_move = self._handle_remote_move
            await self.network_client.initialize_broker_listeners()

    async def _handle_remote_move(self, move_data):
        """Handle remote move received from network client."""
        if move_data:
            self.process_move(move_data)

    def reset_game(self):
        """Reset the game state to initial layout and values."""
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

    def set_game_winner(self, winner):
        """Set the winner and trigger observer notifications for game end."""
        self._runner.status.game_over = True
        self._runner.status.winner = winner
        self._handle_game_end()

    async def wait_for_match_and_listen(self, on_start_callback):
        """Wait for match start signal via network client."""
        if self.network_client:
            await self.network_client.wait_for_match_and_listen(on_start_callback)

    async def listen_for_server_messages(self):
        """Listen for server messages via network client."""
        if self.network_client:
            self.network_client.on_win_by_timeout = self.set_game_winner
            await self.network_client.listen_for_server_messages()