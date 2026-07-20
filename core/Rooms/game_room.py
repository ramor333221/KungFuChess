import asyncio
from config.constants import MSG_TYPE_MOVE


class GameRoom:
    """Manages a specific game session, player identities, and delta updates."""

    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}  # {player_id: {"name": str, "ws": websocket}}
        self.lock = asyncio.Lock()
        self.disconnect_tasks = {}

    def add_player(self, player_id, name, websocket):
        """Registers a player with their name and websocket connection."""
        self.players[player_id] = {"name": name, "ws": websocket}
        print(f"Player {name} added to room {self.room_id}.")

    async def broadcast_move_delta(self, from_pos, to_pos, piece_code):
        """Sends only the changed piece information to all connected clients."""
        delta = {
            "type": MSG_TYPE_MOVE,
            "data": {
                "from": from_pos,
                "to": to_pos,
                "piece": piece_code
            }
        }

        tasks = [
            p_info["ws"].send_json(delta)
            for p_info in self.players.values()
        ]
        if tasks:
            await asyncio.gather(*tasks)

    async def process_move(self, player_id, move_data):
        """Processes a move, updates logic, and broadcasts the resulting delta."""
        async with self.lock:
            await self.broadcast_move_delta(
                move_data['from'],
                move_data['to'],
                move_data.get('piece')
            )