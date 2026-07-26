import json
import asyncio

from config.constants import DEFAULT_PLAYER_NAME, DEFAULT_ELO, DEFAULT_MODE, COLOR_WHITE, COLOR_BLACK, \
    DISCONNECT_TIMEOUT_SECONDS
from src.application.sockets.matchmaker import Matchmaker
from src.utils.logger.logger import setup_logger

logger = setup_logger("ServerLogger", "server_activity.log")




class GameServer:
    """Manages active game rooms, custom room names, passwords, viewers, and disconnections."""
    def __init__(self, matchmaker: Matchmaker):
        self.rooms = {}
        self.player_names = {}
        self.player_elos = {}
        self.websocket_rooms = {}
        self.matchmaker = matchmaker

        self.handlers = {
            'LOGIN': self._handle_login,
            'CREATE_ROOM': self._handle_create_room,
            'JOIN_ROOM': self._handle_join_room,
            'MOVE': self._handle_move
        }

    async def handle_connection(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                logger.info(f"Received message type '{msg_type}' from client.")

                handler = self.handlers.get(msg_type)
                if handler:
                    await handler(websocket, data)
                else:
                    logger.warning(f"Unknown message type received: {msg_type}")

        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            await self._handle_disconnection(websocket)


    async def _handle_login(self, websocket, data):
        username = data.get('username', DEFAULT_PLAYER_NAME)
        elo = data.get('elo', DEFAULT_ELO)
        mode = data.get('mode', DEFAULT_MODE)

        self.player_names[websocket] = username
        self.player_elos[websocket] = elo
        logger.info(f"Player logged in: {username} (ELO: {elo}, Mode: {mode})")

        if mode == DEFAULT_MODE:
            player_session = {
                "username": username,
                "elo": elo,
                "websocket": websocket
            }
            asyncio.create_task(self._process_matchmaking(player_session))

    async def _handle_create_room(self, websocket, data):
        room_name = data.get('room_name')
        password = data.get('password', '')

        if room_name in self.rooms:
            await websocket.send(json.dumps({
                "type": "ERROR",
                "message": f"Room '{room_name}' already exists!"
            }))
        else:
            self.rooms[room_name] = {
                "white": websocket,
                "black": None,
                "viewers": [],
                "password": password,
                "disconnect_task": None
            }
            self.websocket_rooms[websocket] = room_name
            logger.info(f"Room '{room_name}' created by {self.player_names.get(websocket, DEFAULT_PLAYER_NAME)}")

            await websocket.send(json.dumps({
                "type": "ROOM_CREATED",
                "room_name": room_name,
                "color": COLOR_WHITE
            }))

    async def _handle_join_room(self, websocket, data):
        target_room = data.get('room_name')
        password = data.get('password', '')

        if target_room not in self.rooms:
            logger.warning(f"Player attempted to join non-existent room: {target_room}")
            await websocket.send(json.dumps({
                "type": "ERROR",
                "message": f"Room '{target_room}' does not exist!"
            }))
            return

        room = self.rooms[target_room]

        if room["password"] and room["password"] != password:
            logger.warning(f"Incorrect password for room '{target_room}'")
            await websocket.send(json.dumps({
                "type": "ERROR",
                "message": "Incorrect password for this room!"
            }))
            return

        self.websocket_rooms[websocket] = target_room

        if room["black"] is None:
            room["black"] = websocket
            logger.info(f"Player {self.player_names.get(websocket)} joined room '{target_room}' as BLACK.")

            await room[COLOR_WHITE].send(json.dumps({
                "type": "START",
                "color": COLOR_WHITE,
                "room_name": target_room,
                "opponent": self.player_names.get(websocket, DEFAULT_PLAYER_NAME)
            }))
            await websocket.send(json.dumps({
                "type": "START",
                "color": COLOR_BLACK,
                "room_name": target_room,
                "opponent": self.player_names.get(room["white"], DEFAULT_PLAYER_NAME)
            }))
        else:
            room["viewers"].append(websocket)
            logger.info(f"Player {self.player_names.get(websocket)} joined room '{target_room}' as VIEWER.")
            await websocket.send(json.dumps({
                "type": "START_VIEWER",
                "color": "viewer",
                "room_name": target_room
            }))

    async def _handle_move(self, websocket, data):
        room_name = data.get('room_name')
        room = self.rooms.get(room_name)
        if room:
            logger.info(f"MOVE command processed in room '{room_name}'")
            targets = []
            if websocket == room[COLOR_WHITE] and room[COLOR_BLACK]:
                targets.append(room[COLOR_BLACK])
            elif websocket == room[COLOR_BLACK] and room[COLOR_WHITE]:
                targets.append(room[COLOR_WHITE])

            targets.extend(room['viewers'])

            for target in targets:
                await target.send(json.dumps({
                    "type": "MOVE",
                    "data": data['data']
                }))

    async def _process_matchmaking(self, player_session):
        logger.info(f"Player {player_session['username']} entered auto-matchmaking queue.")
        matched_opponent = await self.matchmaker.add_to_queue(player_session)

        if matched_opponent:
            room_name = f"Match_{player_session['username']}_{matched_opponent['username']}"

            p1_ws = player_session["websocket"]
            p2_ws = matched_opponent["websocket"]

            self.rooms[room_name] = {
                "white": p1_ws,
                "black": p2_ws,
                "viewers": [],
                "password": "",
                "disconnect_task": None
            }

            self.websocket_rooms[p1_ws] = room_name
            self.websocket_rooms[p2_ws] = room_name

            await p1_ws.send(json.dumps({
                "type": "START",
                "color": COLOR_WHITE,
                "room_name": room_name,
                "opponent": self.player_names.get(p2_ws, DEFAULT_PLAYER_NAME)
            }))

            await p2_ws.send(json.dumps({
                "type": "START",
                "color": COLOR_BLACK,
                "room_name": room_name,
                "opponent": self.player_names.get(p1_ws, DEFAULT_PLAYER_NAME)
            }))

    async def _handle_disconnection(self, websocket):
        if websocket in self.player_names:
            username = self.player_names[websocket]
            logger.info(f"Player disconnected: {username}")
            await self.matchmaker.remove_from_queue(username)
            del self.player_names[websocket]
            if websocket in self.player_elos:
                del self.player_elos[websocket]

        room_name = self.websocket_rooms.get(websocket)
        if room_name and room_name in self.rooms:
            room = self.rooms[room_name]

            if websocket == room[COLOR_WHITE] or websocket == room[COLOR_BLACK]:
                is_white = (websocket == room[COLOR_WHITE])
                opponent_ws = room[COLOR_BLACK] if is_white else room[COLOR_WHITE]

                if opponent_ws:
                    logger.info(f"Player in room '{room_name}' disconnected. Starting {DISCONNECT_TIMEOUT_SECONDS}s countdown.")
                    await opponent_ws.send(json.dumps({
                        "type": "OPPONENT_DISCONNECTED",
                        "countdown": DISCONNECT_TIMEOUT_SECONDS
                    }))

                    room["disconnect_task"] = asyncio.create_task(
                        self._disconnect_timeout_task(room_name, opponent_ws)
                    )
            elif websocket in room["viewers"]:
                room["viewers"].remove(websocket)

        if websocket in self.websocket_rooms:
            del self.websocket_rooms[websocket]

    async def _disconnect_timeout_task(self, room_name, winner_ws):
        try:
            await asyncio.sleep(DISCONNECT_TIMEOUT_SECONDS)
            if room_name in self.rooms:
                logger.info(f"Room '{room_name}' closed due to timeout. Opponent wins!")
                await winner_ws.send(json.dumps({
                    "type": "WIN_BY_TIMEOUT",
                    "message": "Opponent disconnected for too long. You win!"
                }))
                del self.rooms[room_name]
        except asyncio.CancelledError:
            pass