import json
import uuid
import asyncio

from src.application.sockets.matchmaker import Matchmaker
from src.utils.logger.logger import setup_logger


logger = setup_logger("ServerLogger", "server_activity.log")


class GameServer:
    """Manages active game rooms, custom room IDs, viewers, and disconnection timeouts."""

    def __init__(self):
        """Initializes the game server with empty room tracking, player registries, and the matchmaker."""
        self.rooms = {}
        self.player_names = {}
        self.player_elos = {}
        self.websocket_rooms = {}
        self.matchmaker = Matchmaker()

    async def handle_connection(self, websocket):
        """Manages the lifecycle of a single WebSocket connection[cite: 9]."""
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                logger.info(f"Received message type '{msg_type}' from client[cite: 9].")

                if msg_type == 'LOGIN':
                    username = data.get('username', 'Player')
                    elo = data.get('elo', 1200)

                    self.player_names[websocket] = username
                    self.player_elos[websocket] = elo
                    logger.info(f"Player logged in: {username} with ELO {elo}")

                    player_session = {
                        "username": username,
                        "elo": elo,
                        "websocket": websocket
                    }

                    asyncio.create_task(self._process_matchmaking(player_session))

                elif msg_type == 'MOVE':
                    room_id = data.get('room')
                    room = self.rooms.get(room_id)
                    if room:
                        logger.info(f"MOVE command processed in room {room_id}[cite: 9]")
                        targets = []
                        if websocket == room['white'] and room['black']:
                            targets.append(room['black'])
                        elif websocket == room['black'] and room['white']:
                            targets.append(room['white'])

                        targets.extend(room['viewers'])

                        for target in targets:
                            await target.send(json.dumps({
                                "type": "MOVE",
                                "data": data['data']
                            }))

        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            await self._handle_disconnection(websocket)

    async def _process_matchmaking(self, player_session):
        """Executes the matchmaking loop and starts the room once a match is found."""
        logger.info(f"Player {player_session['username']} entered matchmaking queue.")
        matched_opponent = await self.matchmaker.add_to_queue(player_session)

        if matched_opponent:
            room_id = str(uuid.uuid4())[:8]

            p1_ws = player_session["websocket"]
            p2_ws = matched_opponent["websocket"]

            self.rooms[room_id] = {
                "white": p1_ws,
                "black": p2_ws,
                "viewers": [],
                "disconnect_task": None
            }

            self.websocket_rooms[p1_ws] = room_id
            self.websocket_rooms[p2_ws] = room_id

            await p1_ws.send(json.dumps({
                "type": "START",
                "color": "white",
                "room": room_id,
                "opponent": self.player_names.get(p2_ws, "Player")
            }))

            await p2_ws.send(json.dumps({
                "type": "START",
                "color": "black",
                "room": room_id,
                "opponent": self.player_names.get(p1_ws, "Player")
            }))

            logger.info(f"Auto-match found! Game started in room {room_id} between {player_session['username']} and {matched_opponent['username']}.")

    async def _handle_disconnection(self, websocket):
        """Handles player disconnection cleanup and triggers timeout tasks[cite: 9]."""
        if websocket in self.player_names:
            username = self.player_names[websocket]
            logger.info(f"Player disconnected: {username}")
            await self.matchmaker.remove_from_queue(username)
            del self.player_names[websocket]
            if websocket in self.player_elos:
                del self.player_elos[websocket]

        room_id = self.websocket_rooms.get(websocket)
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]

            if websocket == room["white"] or websocket == room["black"]:
                is_white = (websocket == room["white"])
                opponent_ws = room["black"] if is_white else room["white"]

                if opponent_ws:
                    logger.info(f"Player in room {room_id} disconnected. Starting 20s countdown.")
                    await opponent_ws.send(json.dumps({
                        "type": "OPPONENT_DISCONNECTED",
                        "countdown": 20
                    }))

                    room["disconnect_task"] = asyncio.create_task(
                        self._disconnect_timeout_task(room_id, opponent_ws)
                    )
            elif websocket in room["viewers"]:
                room["viewers"].remove(websocket)

        if websocket in self.websocket_rooms:
            del self.websocket_rooms[websocket]

    async def _disconnect_timeout_task(self, room_id, winner_ws):
        """Waits for the disconnection timeout and declares a timeout win if expired[cite: 9]."""
        try:
            await asyncio.sleep(20)
            if room_id in self.rooms:
                logger.info(f"Room {room_id} closed due to timeout. Opponent wins[cite: 9].")
                await winner_ws.send(json.dumps({
                    "type": "WIN_BY_TIMEOUT",
                    "message": "Opponent disconnected for too long. You win!"
                }))
                del self.rooms[room_id]
        except asyncio.CancelledError:
            pass