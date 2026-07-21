import asyncio
import json
from pathlib import Path

from DB.db_manager import DBManager
from src.GUI.board_controller import BoardController, show_gui_home_screen
from src.application.network.engine_facade import EngineFacade


async def main():
    # 1. Show GUI Login / Room Entry Dialog with Password
    action_type, username, room_name, password = show_gui_home_screen()
    if action_type == "CANCEL":
        print("Cancelled by user.")
        return

    # 2. Setup path assets and engine facade
    project_root = Path(__file__).resolve().parent
    assets_path = project_root / "assests" / "board.png"
    db_manager = DBManager()

    facade = EngineFacade(
        board_path=str(assets_path),
        db_manager=db_manager,
        username=username
    )

    # 3. Connect to WebSocket Server with manual mode
    await facade.connect_to_server("ws://localhost:8765", elo=1200)

    # Send explicit LOGIN message with mode='manual' to avoid auto-queue
    await facade.websocket.send(json.dumps({
        "type": "LOGIN",
        "username": username,
        "elo": 1200,
        "mode": "manual"
    }))

    gui = BoardController(facade, board_path=str(assets_path))
    gui.room_name = room_name

    # 4. Transmit CREATE or JOIN command including Password
    if action_type == "CREATE":
        await facade.websocket.send(json.dumps({
            "type": "CREATE_ROOM",
            "room_name": room_name,
            "password": password
        }))
    elif action_type == "JOIN":
        await facade.websocket.send(json.dumps({
            "type": "JOIN_ROOM",
            "room_name": room_name,
            "password": password
        }))

    # 5. Start listening and main window
    await gui.start_game_when_matched()


if __name__ == "__main__":
    asyncio.run(main())