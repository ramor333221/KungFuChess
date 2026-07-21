import json
import websockets

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

    def __init__(self, board_path, db_manager, board_matrix=None, player_color=None, username="Player", message_broker=None):
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
        self.broker = message_broker
        self.room_name = None
        self.on_server_message = None
        self.on_opponent_disconnect = None
        self._runner.status.on_game_over = self._handle_game_end

        self.attach(ScoreObserver(self.db_manager))
        self.attach(MoveLoggerObserver())
        self.attach(AchievementObserver())
        self.attach(SoundObserver())

        if board_matrix is None:
            board_matrix = BoardFactory.get_default_layout()

        self._runner.run_game(board_matrix, [])

    async def connect_to_server(self, uri="ws://localhost:8765", elo=1200):
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(json.dumps({
            "type": "LOGIN",
            "username": self.username,
            "elo": elo
        }))

    async def send_move(self, move_data):
        if self.websocket:
            payload = {
                "type": "MOVE",
                "data": move_data
            }
            if self.room_name:
                payload["room_name"] = self.room_name
            await self.websocket.send(json.dumps(payload))

        if self.broker:
            await self.broker.publish(constants.TOPIC_PLAYER_MOVE, move_data)

    def process_move(self, command_str):
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
        if hasattr(self._runner, 'board') and self._runner.board is not None:
            return self._runner.board.matrix
        return [[None for _ in range(constants.BOARD_SIZE)] for _ in range(constants.BOARD_SIZE)]

    def get_valid_moves(self, row, col):
        return self._runner.get_possible_moves(row, col)

    def get_game_over_status(self):
        return getattr(self._runner.status, 'game_over', False)

    def switch_player_turn(self):
        self._runner.status.selected_pos = None
        self._runner.status.switch_turn()

    async def initialize_broker_listeners(self):
        if self.broker:
            await self.broker.subscribe(constants.TOPIC_OPPONENT_MOVE, self._handle_remote_move)

    async def _handle_remote_move(self, move_data):
        if move_data:
            self.process_move(move_data)

    def reset_game(self):
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
                    room_id = data.get('room') or data.get('room_name')
                    self.room_name = room_id

                    await on_start_callback(room_id)
                    break
        except Exception:
            if self.on_opponent_disconnect:
                self.on_opponent_disconnect()

    async def listen_for_server_messages(self):
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                if message is None:
                    continue

                data = json.loads(message)
                msg_type = data.get('type')

                if self.on_server_message:
                    self.on_server_message(data)

                if msg_type == 'MOVE':
                    if self.broker:
                        await self.broker.publish(constants.TOPIC_OPPONENT_MOVE, data.get('data'))
                elif msg_type in ('OPPONENT_DISCONNECTED', 'DISCONNECT'):
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()

        except Exception:
            if self.on_opponent_disconnect:
                self.on_opponent_disconnect()