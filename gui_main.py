import asyncio
import websockets
import json
from GUI.board_controller import BoardController
from application.network.engine_facade import EngineFacade


async def start_client():
    """Initializes the websocket connection and sets up the game environment."""
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send(json.dumps({"type": "LOGIN", "player": "Player"}))
        msg = await websocket.recv()
        data = json.loads(msg)

        if data['type'] == 'START':
            facade = EngineFacade(board_path="board.png", player_color=data['color'])
            facade.websocket = websocket

            gui = BoardController(facade, "board.png")
            gui.set_room_id(data['room'])

            asyncio.create_task(facade.listen_for_moves(gui.on_opponent_move))
            await gui.run_async()


if __name__ == "__main__":
    asyncio.run(start_client())