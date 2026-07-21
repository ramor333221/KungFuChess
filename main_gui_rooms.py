import asyncio
from pathlib import Path
import json

from DB.db_manager import DBManager
from src.GUI.board_controller import BoardController
from src.application.auth.auth_handler import AuthHandler
from src.application.network.engine_facade import EngineFacade


async def start_gui_room_system(username):
    project_root = Path("C:/Users/User/Downloads/ChessCTD")
    assets_path = project_root / "assests" / "board.png"
    db_manager = DBManager()

    facade = EngineFacade(
        board_path=str(assets_path),
        db_manager=db_manager,
        username=username
    )

    await facade.connect_to_server("ws://localhost:8765")
    gui = BoardController(facade, board_path=None)

    # פתיחת חלון תפריט הבית לבחירת Create / Join / Cancel
    action, room_id = gui.show_home_screen()

    if action == "CREATE":
        await facade.websocket.send(json.dumps({"type": "CREATE_ROOM"}))
        print("[GUI Room] Room creation requested. Waiting for opponent...")
    elif action == "JOIN":
        gui.set_room_id(room_id)
        await facade.websocket.send(json.dumps({"type": "JOIN_ROOM", "room": room_id}))
        print(f"[GUI Room] Joining room {room_id}...")
    else:
        print("[GUI Room] Action cancelled.")
        return

    # האזנה לתשובות השרת לפתיחת הלוח כששחקנים או צופים מחוברים
    async for message in facade.websocket:
        if message is None:
            continue

        data = json.loads(message)
        msg_type = data.get('type')

        if msg_type == 'ROOM_CREATED':
            r_id = data.get('room')
            gui.set_room_id(r_id)
            print(f"[GUI Room] Room ID generated: {r_id} (Share this ID with your opponent)")

        elif msg_type == 'START' or msg_type == 'START_VIEWER':
            facade.player_color = data.get('color', 'viewer')
            assigned_room = data.get('room')
            if assigned_room:
                gui.set_room_id(assigned_room)

            facade.opponent_username = data.get('opponent', "Unknown_Opponent")
            print(f"\n[GUI Room] Room ready! Launching board view...")

            asyncio.create_task(facade.listen_for_moves(gui.handle_server_message))
            await gui.run_async()
            break
        else:
            gui.handle_server_message(data)


if __name__ == "__main__":
    auth = AuthHandler()
    user_info = auth.login()
    if user_info:
        asyncio.run(start_gui_room_system(user_info['username']))
    else:
        print("Login failed.")