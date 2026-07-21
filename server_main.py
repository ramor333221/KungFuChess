import asyncio
import websockets
from src.application.sockets.game_server import GameServer


async def run_server():
    """Initializes and runs the websocket server for game communication."""
    server = GameServer()
    async with websockets.serve(server.handle_connection, "localhost", 8765):
        print("Server started on ws://localhost:8765. Waiting for players...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(run_server())