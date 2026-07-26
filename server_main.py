import asyncio
import websockets
from config.constants import SERVER_HOST, SERVER_PORT
from src.application.sockets.game_server import GameServer
from src.application.sockets.matchmaker import Matchmaker

async def run_server():
    """Initializes and runs the websocket server using centralized configuration."""
    shared_matchmaker = Matchmaker()
    server = GameServer(shared_matchmaker)
    async with websockets.serve(server.handle_connection, SERVER_HOST, SERVER_PORT):
        print(f"Server started on ws://{SERVER_HOST}:{SERVER_PORT}. Waiting for players...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run_server())