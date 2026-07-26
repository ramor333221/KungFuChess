import json
import asyncio
import websockets
import websockets.exceptions
from config import constants
from config.constants import TRIAL, MAX_TRIAL
from src.utils.logger.logger import setup_logger

logger = setup_logger("ClientLogger", "client_activity.log")


class GameNetworkClient:
    """Manages WebSocket connections, server message listeners, and message broadcasting with auto-reconnect."""

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
        self._uri = constants.DEFAULT_WS_URI
        self._elo = constants.DEFAULT_ELO
        self._is_running = True

    async def connect_to_server(self, uri=constants.DEFAULT_WS_URI, elo=constants.DEFAULT_ELO):
        """Establish a WebSocket connection to the game server and send login payload."""
        self._uri = uri
        self._elo = elo
        self.websocket = await websockets.connect(uri)
        await self.websocket.send(json.dumps({
            "type": constants.MSG_TYPE_LOGIN,
            "username": self.username,
            "elo": elo
        }))
        logger.info(f"Connected to server at {uri} as {self.username}")

    async def _reconnect(self):
        """Attempt to reconnect to the server with a backoff delay."""
        attempt = TRIAL
        max_attempts = MAX_TRIAL
        while self._is_running and attempt <= max_attempts:
            try:
                logger.info(f"Attempting to reconnect ({attempt}/{max_attempts})...")
                await asyncio.sleep(3 * attempt)
                self.websocket = await websockets.connect(self._uri)
                await self.websocket.send(json.dumps({
                    "type": constants.MSG_TYPE_LOGIN,
                    "username": self.username,
                    "elo": self._elo
                }))
                logger.info("Successfully reconnected to the server.")
                return True
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt} failed: {e}")
                attempt += 1
        return False

    async def send_move(self, move_data):
        """Send a move payload to the server and publish to the message broker."""
        if self.websocket:
            payload = {
                "type": constants.MSG_TYPE_MOVE,
                "data": move_data
            }
            if self.room_name:
                payload["room_name"] = self.room_name
            try:
                await self.websocket.send(json.dumps(payload))
            except websockets.exceptions.ConnectionClosed:
                logger.error("Failed to send move: WebSocket connection is closed.")

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
        """Wait for the server match start signal with connection drop resilience."""
        if not self.websocket:
            return

        while self._is_running:
            try:
                async for message in self.websocket:
                    if message is None:
                        continue

                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON message during matchmaking: {e} | Message: {message}")
                        continue

                    msg_type = data.get('type')

                    if msg_type in (constants.MSG_TYPE_START, constants.MSG_TYPE_ROOM_CREATED,
                                    constants.MSG_TYPE_START_VIEWER):
                        self.player_color = data.get('color', constants.COLOR_WHITE)
                        self.opponent_username = data.get('opponent', constants.UNKNOWN_OPPONENT)
                        room_id = data.get('room') or data.get('room_name')
                        self.room_name = room_id

                        await on_start_callback(room_id)
                        return

            except websockets.exceptions.ConnectionClosed as e:
                logger.info(f"WebSocket connection closed during matchmaking: {e}")
                reconnected = await self._reconnect()
                if not reconnected:
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()
                    break
            except Exception as e:
                logger.exception(f"Unexpected error in wait_for_match_and_listen: {e}")
                if self.on_opponent_disconnect:
                    self.on_opponent_disconnect()
                break

    async def listen_for_server_messages(self):
        """Continuously listen for incoming server messages with auto-reconnect logic."""
        if not self.websocket:
            return

        while self._is_running:
            try:
                async for message in self.websocket:
                    if message is None:
                        continue

                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse incoming server message: {e} | Message: {message}")
                        continue

                    msg_type = data.get('type')

                    if self.on_server_message:
                        try:
                            self.on_server_message(data)
                        except Exception as callback_err:
                            logger.error(f"Error executing on_server_message callback: {callback_err}")

                    if msg_type == constants.MSG_TYPE_MOVE:
                        if self.broker:
                            await self.broker.publish(constants.TOPIC_OPPONENT_MOVE, data.get('data'))
                    elif msg_type in (constants.MSG_TYPE_OPPONENT_DISCONNECTED, constants.MSG_TYPE_DISCONNECT):
                        if self.on_opponent_disconnect:
                            self.on_opponent_disconnect()

                    elif msg_type == constants.MSG_TYPE_WIN_BY_TIMEOUT:
                        if self.on_win_by_timeout:
                            self.on_win_by_timeout(self.player_color)

            except websockets.exceptions.ConnectionClosed as e:
                logger.info(f"WebSocket connection lost: {e}. Attempting recovery...")
                reconnected = await self._reconnect()
                if not reconnected:
                    logger.error("Could not recover connection. Triggering opponent disconnect handler.")
                    if self.on_opponent_disconnect:
                        self.on_opponent_disconnect()
                    break
            except Exception as e:
                logger.exception(f"Critical unexpected error in message listener loop: {e}")
                if self.on_opponent_disconnect:
                    self.on_opponent_disconnect()
                break