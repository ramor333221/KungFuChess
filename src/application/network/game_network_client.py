import json
import websockets
from config import constants


class GameNetworkClient:
    """Manages WebSocket connections, server message listeners, and message broadcasting."""

    def __init__(self, username, room_name=None, message_broker=None):
        self.username = username
        self.room_name = room_name
        self.broker = message_broker
        self.websocket = None
        self.opponent_username = constants.UNKNOWN_OPPONENT
        self.player_color = None
        self.on_server_message = None
        self.on_opponent_disconnect = None
        self.on_win_by_timeout = None
        self.on_remote_move = None

    async def connect_to_server(self, uri=constants.DEFAULT_WS_URI, elo=constants.DEFAULT_ELO):
        """Establish a WebSocket connection to the game server and send login payload."""
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(json.dumps({
            "type": constants.MSG_TYPE_LOGIN,
            "username": self.username,
            "elo": elo
        }))

    async def send_move(self, move_data):
        """Send a move payload to the server and publish to the message broker."""
        if self.websocket:
            payload = {
                "type": constants.MSG_TYPE_MOVE,
                "data": move_data
            }
            if self.room_name:
                payload["room_name"] = self.room_name
            await self.websocket.send(json.dumps(payload))

        if self.broker:
            await self.broker.publish(constants.TOPIC_PLAYER_MOVE, move_data)

    async def initialize_broker_listeners(self):
        """Subscribe to broker topics for opponent moves."""
        if self.broker:
            await self.broker.subscribe(constants.TOPIC_OPPONENT_MOVE, self._handle_remote_move)

    async def _handle_remote_move(self, move_data):
        """Internal callback for handling remote opponent moves from the broker."""
        if move_data and self.on_remote_move:
            await self.on_remote_move(move_data)

    async def wait_for_match_and_listen(self, on_start_callback):
        """Wait for the server match start signal, room creation, or viewer start and trigger callback."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                if message is None:
                    continue

                data = json.loads(message)
                msg_type = data.get('type')

                # Listen for start, room creation, or viewer start signals
                if msg_type in (constants.MSG_TYPE_START, constants.MSG_TYPE_ROOM_CREATED,
                                constants.MSG_TYPE_START_VIEWER):
                    self.player_color = data.get('color', constants.COLOR_WHITE)
                    self.opponent_username = data.get('opponent', constants.UNKNOWN_OPPONENT)
                    room_id = data.get('room') or data.get('room_name')
                    self.room_name = room_id

                    await on_start_callback(room_id)
                    break
        except Exception:
            if self.on_opponent_disconnect:
                self.on_opponent_disconnect()

    async def listen_for_server_messages(self):
        """Continuously listen for incoming server messages via WebSocket."""
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

                if msg_type == constants.MSG_TYPE_MOVE:
                    if self.broker:
                        await self.broker.publish(constants.TOPIC_OPPONENT_MOVE, data.get('data'))
                elif msg_type in (constants.MSG_TYPE_OPPONENT_DISCONNECTED, constants.MSG_TYPE_DISCONNECT):
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()

                elif msg_type == constants.MSG_TYPE_WIN_BY_TIMEOUT:
                    if self.on_win_by_timeout:
                        self.on_win_by_timeout(self.player_color)

        except Exception:
            if self.on_opponent_disconnect:
                self.on_opponent_disconnect()