import asyncio
import json
import websockets
import websockets.exceptions
from config import constants
from config.constants import TRIAL, MAX_TRIAL, RECONNECT_BACKOFF_SECONDS
from src.utils.logger.logger import setup_logger
from shared.domain import MoveCommand
from shared.messages import LoginMessage, MoveMessage

logger = setup_logger("ClientLogger", "client_activity.log")


class WebSocketTransport:
    """Sub-layer 1: Transport Layer - Manages raw WebSocket connection lifecycle and raw frame transmission."""

    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self._is_connected = False

    async def connect(self):
        """Establish the raw WebSocket connection."""
        self.websocket = await websockets.connect(self.uri)
        self._is_connected = True

    async def send(self, raw_message: str):
        """Send raw string payloads over the socket."""
        if self.websocket and self._is_connected:
            await self.websocket.send(raw_message)

    async def receive_frames(self):
        """Async generator yielding raw messages from the transport stream."""
        if self.websocket:
            async for message in self.websocket:
                yield message

    async def close(self):
        """Close the transport connection cleanly."""
        if self.websocket:
            await self.websocket.close()
            self._is_connected = False


class NetworkProtocolCodec:
    """Sub-layer 2: Protocol / Serialization Layer - Handles DTO encoding and decoding."""

    @staticmethod
    def encode_login(username: str, elo: int) -> str:
        return LoginMessage(username=username, elo=elo).to_json()

    @staticmethod
    def encode_move(move_command: MoveCommand, room_name: str = None) -> str:
        return MoveMessage.from_move_command(move_command, room_name).to_json()

    @staticmethod
    def decode_message(raw_message: str) -> dict:
        return json.loads(raw_message)


class GameNetworkClient:
    """Sub-layer 3: Application / Broker Integration Layer - Coordinates transport, protocol, and broker events."""

    def __init__(self, username, room_name=None, message_broker=None):
        self.username = username
        self.room_name = room_name
        self.broker = message_broker
        self.opponent_username = constants.UNKNOWN_OPPONENT
        self.player_color = None

        # Callbacks
        self.on_server_message = None
        self.on_opponent_disconnect = None
        self.on_win_by_timeout = None
        self.on_remote_move = None

        self._uri = constants.DEFAULT_WS_URI
        self._elo = constants.DEFAULT_ELO
        self._is_running = True

        # Instantiate sub-layers
        self.transport = WebSocketTransport(self._uri)
        self.codec = NetworkProtocolCodec()

    async def connect_to_server(self, uri=constants.DEFAULT_WS_URI, elo=constants.DEFAULT_ELO):
        """Initialize connection through transport and authenticate via protocol codec."""
        self._uri = uri
        self._elo = elo
        self.transport = WebSocketTransport(self._uri)

        await self.transport.connect()
        login_payload = self.codec.encode_login(self.username, self._elo)
        await self.transport.send(login_payload)
        logger.info(f"Connected to server at {uri} as {self.username}")

    async def _reconnect(self) -> bool:
        """Attempt recovery with backoff policy using clean constants."""
        attempt = TRIAL
        max_attempts = MAX_TRIAL
        while self._is_running and attempt <= max_attempts:
            try:
                logger.info(f"Attempting reconnection ({attempt}/{max_attempts})...")
                await asyncio.sleep(RECONNECT_BACKOFF_SECONDS * attempt)

                await self.transport.connect()
                login_payload = self.codec.encode_login(self.username, self._elo)
                await self.transport.send(login_payload)

                logger.info("Successfully reconnected to the server.")
                return True
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt} failed: {e}")
                attempt += 1
        return False

    async def send_move(self, move_command: MoveCommand):
        """Serialize move through protocol layer, send via transport, and publish to local broker."""
        if self.transport:
            payload = self.codec.encode_move(move_command, self.room_name)
            try:
                await self.transport.send(payload)
            except websockets.exceptions.ConnectionClosed:
                logger.error("Failed to send move: Transport connection is closed.")

        if self.broker:
            await self.broker.publish(constants.TOPIC_PLAYER_MOVE, move_command)

    async def initialize_broker_listeners(self):
        """Register application event handlers with the message broker."""
        if self.broker:
            await self.broker.subscribe(constants.TOPIC_OPPONENT_MOVE, self._handle_remote_move)

    async def _handle_remote_move(self, move_command: MoveCommand):
        """Handle incoming remote move event."""
        if move_command and self.on_remote_move:
            await self.on_remote_move(move_command)

    async def wait_for_match_and_listen(self, on_start_callback):
        """Matchmaking loop utilizing transport and protocol sub-layers."""
        while self._is_running:
            try:
                async for raw_msg in self.transport.receive_frames():
                    if not raw_msg:
                        continue

                    try:
                        # Delegated to protocol codec layer
                        data = self.codec.decode_message(raw_msg)
                    except json.JSONDecodeError as e:
                        logger.error(f"Protocol decode error during matchmaking: {e}")
                        continue

                    msg_type = data.get('type')

                    if msg_type == constants.MSG_TYPE_ROOM_CREATED:
                        self.room_name = data.get('room') or data.get('room_name')
                        self.player_color = data.get('color', constants.COLOR_WHITE)
                        logger.info(f"Room '{self.room_name}' created. Awaiting opponent...")
                        continue

                    if msg_type in (constants.MSG_TYPE_START, constants.MSG_TYPE_START_VIEWER):
                        self.player_color = data.get('color', constants.COLOR_WHITE)
                        self.opponent_username = data.get('opponent', constants.UNKNOWN_OPPONENT)
                        self.room_name = data.get('room') or data.get('room_name')
                        await on_start_callback(self.room_name)
                        return

            except websockets.exceptions.ConnectionClosed:
                if not await self._reconnect():
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()
                    break
            except Exception as e:
                logger.exception(f"Unexpected error in matchmaking listener: {e}")
                if self.on_opponent_disconnect:
                    self.on_opponent_disconnect()
                break

    async def listen_for_server_messages(self):
        """Main gameplay message loop with clean boundary separation."""
        while self._is_running:
            try:
                async for raw_msg in self.transport.receive_frames():
                    if not raw_msg:
                        continue

                    try:
                        # Delegated to protocol codec layer
                        data = self.codec.decode_message(raw_msg)
                    except json.JSONDecodeError as e:
                        logger.error(f"Protocol decode error: {e}")
                        continue

                    msg_type = data.get('type')

                    if self.on_server_message:
                        try:
                            self.on_server_message(data)
                        except Exception as cb_err:
                            logger.error(f"Callback error in on_server_message: {cb_err}")

                    if msg_type == constants.MSG_TYPE_MOVE:
                        if self.broker:
                            move_msg = MoveMessage.from_json(raw_msg)
                            await self.broker.publish(constants.TOPIC_OPPONENT_MOVE, move_msg.get_move_command())
                    elif msg_type in (constants.MSG_TYPE_OPPONENT_DISCONNECTED, constants.MSG_TYPE_DISCONNECT):
                        if self.on_opponent_disconnect:
                            self.on_opponent_disconnect()
                    elif msg_type == constants.MSG_TYPE_WIN_BY_TIMEOUT:
                        if self.on_win_by_timeout:
                            self.on_win_by_timeout(self.player_color)

            except websockets.exceptions.ConnectionClosed:
                if not await self._reconnect():
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()
                    break
            except Exception as e:
                logger.exception(f"Critical error in message listener loop: {e}")
                if self.on_opponent_disconnect:
                    self.on_opponent_disconnect()
                break