from DB.db_manager import DBManager
from config import constants
from src.core.game_runner import GameRunner
from src.utils.input.BoardFactory import BoardFactory
from src.utils.observer.achievement_observer import AchievementObserver
from src.utils.observer.move_observer import MoveLoggerObserver
from src.utils.observer.observer import Subject
from src.utils.observer.score_observer import ScoreObserver
from shared.domain import MoveCommand
from src.utils.observer.sound_observer import GameOverSoundObserver, MoveSoundObserver


class EngineFacade(Subject):
    """Facade class bridging the GUI with the game engine logic (strictly decoupled from UI and image loading)."""

    def __init__(self, board_matrix=None, player_color=None, username="Player", network_client=None):
        super().__init__()
        self._runner = GameRunner()
        self.db_manager = DBManager()
        self.username = username
        self.network_client = network_client
        self._player_color = player_color
        self._board = board_matrix

        self._runner.status.on_game_over = self._handle_game_end

        self.attach(constants.EVENT_GAME_OVER, ScoreObserver(self.db_manager))
        self.attach(constants.EVENT_MOVE_COMPLETED, MoveLoggerObserver())
        self.attach(constants.EVENT_GAME_OVER, AchievementObserver())
        self.attach(constants.EVENT_MOVE_COMPLETED, MoveSoundObserver())
        self.attach(constants.EVENT_GAME_OVER, GameOverSoundObserver())

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    @property
    def websocket(self):
        """Proxy property for network client websocket with safe fallback."""
        if not self.network_client:
            return None
        return getattr(self.network_client, 'websocket', getattr(self.network_client, 'ws', None))

    @websocket.setter
    def websocket(self, value):
        """Proxy setter for network client websocket with safe fallback."""
        if self.network_client:
            if hasattr(self.network_client, 'websocket'):
                self.network_client.websocket = value
            elif hasattr(self.network_client, 'ws'):
                self.network_client.ws = value
            else:
                setattr(self.network_client, 'websocket', value)

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

    async def send_move(self, move_command: MoveCommand):
        """Send a strongly-typed move command via the network client."""
        if self.network_client:
            await self.network_client.send_move(move_command)

    def process_move(self, move_command: MoveCommand):
        """Process a strongly-typed game move command and notify observers."""
        if not move_command:
            return None

        from_r = move_command.from_row
        from_c = move_command.from_col
        to_r = move_command.to_row
        to_c = move_command.to_col

        try:
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

        command_str = f"{constants.COMMAND_CLICK} {from_r} {from_c} {to_r} {to_c}"
        self._runner.status.add_history(player_id, command_str)

        result = self._runner.interaction_ctrl.execute_command(
            constants.COMMAND_CLICK,
            [str(from_r), str(from_c), str(to_r), str(to_c)]
        )

        if not getattr(self._runner.status, constants.ATTR_GAME_OVER, False):
            self.notify(constants.EVENT_MOVE_COMPLETED, {"data": move_command})

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

    async def _handle_remote_move(self, move_command: MoveCommand):
        """Handle remote move command received from a network client."""
        if move_command:
            self.process_move(move_command)

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
        """Wait for match start signal via a network client."""
        if self.network_client:
            await self.network_client.wait_for_match_and_listen(on_start_callback)

    async def listen_for_server_messages(self):
        """Listen for server messages via network client."""
        if self.network_client:
            self.network_client.on_win_by_timeout = self.set_game_winner
            await self.network_client.listen_for_server_messages()