import cv2
import asyncio
import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from src.GUI.input_handler import InputHandler
from src.GUI.renderer import Renderer
from src.utils.UI.animation_manager import AnimationManager
from src.utils.UI.img import Img
from src.utils.logger.logger import setup_logger
from src.utils.observer.observer import Observer
from config import constants

client_logger = setup_logger("ClientLogger", "client_activity.log")


def show_gui_home_screen() -> tuple[str, str, str, str]:
    """
    Displays a graphical popup collecting Username, Room Name, and Password
    with Create / Join / Cancel buttons.
    Returns: (action_type, username, room_name, password)
    """
    root = tk.Tk()
    root.title("Chess Room Portal")
    root.geometry("340x320")
    root.resizable(False, False)

    action = {"type": "CANCEL", "username": "", "room_name": "", "password": ""}

    tk.Label(root, text="Welcome to Chess", font=("Arial", 12, "bold")).pack(pady=8)

    # Username Field
    tk.Label(root, text="Username:").pack()
    user_entry = tk.Entry(root, width=28)
    user_entry.pack(pady=3)
    user_entry.insert(0, "Player1")

    # Room Name Field
    tk.Label(root, text="Room Name:").pack()
    room_entry = tk.Entry(root, width=28)
    room_entry.pack(pady=3)

    # Password Field
    tk.Label(root, text="Password (Optional/Required):").pack()
    pass_entry = tk.Entry(root, width=28, show="*")
    pass_entry.pack(pady=3)

    def validate_inputs() -> tuple[str, str, str] | None:
        username = user_entry.get().strip()
        room_name = room_entry.get().strip()
        password = pass_entry.get().strip()

        if not username:
            messagebox.showwarning("Input Error", "Please enter a Username!")
            return None
        if not room_name:
            messagebox.showwarning("Input Error", "Please enter a Room Name!")
            return None
        return username, room_name, password

    def on_create():
        inputs = validate_inputs()
        if inputs:
            action["type"] = "CREATE"
            action["username"], action["room_name"], action["password"] = inputs
            root.destroy()

    def on_join():
        inputs = validate_inputs()
        if inputs:
            action["type"] = "JOIN"
            action["username"], action["room_name"], action["password"] = inputs
            root.destroy()

    def on_cancel():
        action["type"] = "CANCEL"
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=12)

    tk.Button(btn_frame, text="Create", width=9, command=on_create).grid(row=0, column=0, padx=4)
    tk.Button(btn_frame, text="Join", width=9, command=on_join).grid(row=0, column=1, padx=4)
    tk.Button(btn_frame, text="Cancel", width=9, command=on_cancel).grid(row=0, column=2, padx=4)

    root.mainloop()
    return action["type"], action["username"], action["room_name"], action["password"]


class BoardController(Observer):
    """Manages game GUI, room state, disconnect timers, and server messages."""

    def __init__(self, facade, board_path: str = None):
        self.facade = facade
        self.player_color = facade.player_color
        self.facade.attach(self)

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.board_base = self._load_board_image(board_path)

        self.piece_animations = {}
        self.selected_square = None
        self.room_name = None

        self.disconnect_countdown = None
        self.win_message = None

        self.renderer = Renderer(facade, player_color=self.player_color)
        self.input_handler = InputHandler(
            facade=facade,
            renderer=self.renderer,
            on_board_click=self.handle_click
        )

        self._load_animations()
        client_logger.info("BoardController initialized successfully.")

    def update(self, event, data):
        if event == constants.EVENT_MOVE_COMPLETED:
            client_logger.info(f"Move completed: {data}")

    def handle_server_message(self, message_data: dict):
        msg_type = message_data.get('type')
        client_logger.info(f"Received server message type: {msg_type}")

        if msg_type == 'ROOM_CREATED':
            self.room_name = message_data.get('room_name')
            self.player_color = message_data.get('color', 'white')
            client_logger.info(f"Room Created: {self.room_name}")

        elif msg_type == 'START':
            self.room_name = message_data.get('room_name')
            self.player_color = message_data.get('color', self.player_color)
            self.renderer.player_color = self.player_color
            client_logger.info(f"Game started in room {self.room_name} as {self.player_color}")

        elif msg_type == 'START_VIEWER':
            self.room_name = message_data.get('room_name')
            self.player_color = 'viewer'
            client_logger.info(f"Joined room {self.room_name} as spectator.")

        elif msg_type == 'MOVE':
            move_data = message_data.get('data')
            if move_data:
                self.facade.process_move(move_data)

        elif msg_type == 'OPPONENT_DISCONNECTED':
            self.disconnect_countdown = message_data.get('countdown', 20)
            client_logger.warning("Opponent disconnected! Starting 20s visual countdown.")

        elif msg_type == 'WIN_BY_TIMEOUT':
            client_logger.info("Won game due to opponent timeout.")
            self.win_message = message_data.get('message', "Opponent disconnected. You Win!")
            print(self.win_message)
            self.disconnect_countdown = -1

        elif msg_type == 'ERROR':
            print(f"Error: {message_data.get('message')}")

    def _initialize_window(self):
        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.input_handler.handle_event)

    def _load_board_image(self, board_path):
        path = Path(board_path) if board_path else self.project_root / "assests" / "board.png"
        return Img().read(path)

    def handle_click(self, row, col):
        if self.player_color == 'black':
            row, col = 7 - row, 7 - col

        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        if self.selected_square is None:
            if self._is_player_piece(token):
                self.selected_square = (row, col)
        else:
            self._handle_move_execution(row, col)

    def _is_player_piece(self, token):
        if not token or token == constants.EMPTY_CELL or not isinstance(token, str):
            return False
        if self.player_color == 'white' and "W" in token:
            return True
        if self.player_color == 'black' and "B" in token:
            return True
        return False

    def _handle_move_execution(self, row, col):
        valid_moves = self.facade.get_valid_moves(self.selected_square[0], self.selected_square[1])

        if (row, col) in valid_moves:
            move_cmd = f"click {self.selected_square[0]} {self.selected_square[1]} {row} {col}"
            self.facade.process_move(move_cmd)

            if self.facade.websocket and self.room_name:
                asyncio.create_task(self.facade.websocket.send(json.dumps({
                    "type": "MOVE", "room_name": self.room_name, "data": move_cmd
                })))

        self.selected_square = None

    def _load_animations(self):
        base_path = self.project_root / "assests" / "piece_mine"
        if base_path.exists():
            for folder in base_path.iterdir():
                if folder.is_dir() and (path := folder / "states" / "idle").exists():
                    manager = AnimationManager(path)
                    size = int(self.facade.mapper.cell_size * 0.65)
                    for frame in manager.frames:
                        frame.img = cv2.resize(frame.img, (size, size), interpolation=cv2.INTER_AREA)
                    self.piece_animations[folder.name] = manager

    async def start_game_when_matched(self):
        await self.facade.wait_for_match_and_listen(self._on_match_started)

    async def _on_match_started(self, room_name):
        if room_name:
            self.room_name = room_name

        self.player_color = self.facade.player_color
        self.renderer.player_color = self.player_color

        self._initialize_window()
        asyncio.create_task(self.facade.listen_for_moves(self.handle_server_message))
        await self.run_async()

    async def run_async(self):
        last_time = cv2.getTickCount()
        timer_accumulator = 0

        while True:
            if self.disconnect_countdown == -1:
                client_logger.info("Closing window following timeout victory.")
                await asyncio.sleep(2)
                break

            now = cv2.getTickCount()
            delta_ms = int((now - last_time) * 1000 / cv2.getTickFrequency())
            last_time = now

            if self.disconnect_countdown is not None and self.disconnect_countdown > 0:
                timer_accumulator += delta_ms
                if timer_accumulator >= 1000:
                    self.disconnect_countdown -= 1
                    timer_accumulator = 0

            self.facade._runner.interaction_ctrl.manager.process_time_tick(delta_ms)
            canvas = self.renderer.render(self.board_base.img, self.piece_animations, self.selected_square)
            img_canvas = canvas.img if hasattr(canvas, 'img') else canvas

            if self.room_name:
                cv2.putText(
                    img_canvas,
                    f"Room: {self.room_name}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

            if self.disconnect_countdown is not None and self.disconnect_countdown > 0:
                cv2.putText(
                    img_canvas,
                    f"Opponent Disconnected! Auto-win in: {self.disconnect_countdown}s",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

            cv2.imshow("Main Board", img_canvas)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await asyncio.sleep(0.01)

        cv2.destroyAllWindows()