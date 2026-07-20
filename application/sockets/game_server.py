import asyncio
import json
import uuid
import websockets


class GameServer:
    """Manages active game rooms and player matchmaking."""

    def __init__(self):
        self.rooms = {}
        self.waiting_player = None

    async def handle_connection(self, websocket):
        """Manages the lifecycle of a single WebSocket connection."""
        try:
            async for message in websocket:
                data = json.loads(message)

                if data['type'] == 'LOGIN':
                    if self.waiting_player is None:
                        self.waiting_player = websocket
                    else:
                        room_id = str(uuid.uuid4())
                        self.rooms[room_id] = {"white": self.waiting_player, "black": websocket}
                        await self.waiting_player.send(json.dumps({"type": "START", "color": "white", "room": room_id}))
                        await websocket.send(json.dumps({"type": "START", "color": "black", "room": room_id}))
                        self.waiting_player = None

                elif data['type'] == 'MOVE':
                    room_id = data.get('room')
                    room = self.rooms.get(room_id)
                    if room:
                        target = room['black'] if websocket == room['white'] else room['white']
                        await target.send(json.dumps({"type": "MOVE", "data": data['data']}))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.waiting_player == websocket:
                self.waiting_player = None


async def run_server():
    """Sets up and starts the WebSocket server listener."""
    server = GameServer()
    async with websockets.serve(server.handle_connection, "localhost", 8765, ping_interval=20, ping_timeout=20):
        await asyncio.Future()