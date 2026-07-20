import cv2
import asyncio
import json
from pathlib import Path
from GUI.input_handler import InputHandler
from GUI.renderer import Renderer
from config import constants
from utils.UI.animation_manager import AnimationManager
from utils.UI.img import Img


class BoardController:
    """Manages the game board GUI, player input, and synchronization with the server."""

    def __init__(self, facade, board_path: str):
        """Initializes the board, rendering settings, and event handling."""
        self.facade = facade
        self.player_color = facade.player_color
        self.board_base = Img().read(board_path)
        self.piece_animations = {}
        self.selected_square = None
        self.room_id = None

        self.renderer = Renderer(facade, player_color=self.player_color)

        self.input_handler = InputHandler(
            facade=facade,
            renderer=self.renderer,
            on_board_click=self.handle_click
        )

        self._load_animations()
        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.input_handler.handle_event)

    def handle_click(self, row, col):
        """Processes board clicks, enforces turn validation, and handles move transmission."""
        if self.player_color == 'black':
            row, col = 7 - row, 7 - col

        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        turn_id = self.facade._runner.status.current_turn
        my_turn = (self.player_color == 'white' and turn_id == constants.PLAYER_WHITE) or \
                  (self.player_color == 'black' and turn_id == constants.PLAYER_BLACK)

        if not my_turn:
            return

        if self.selected_square is None:
            if token and token != constants.EMPTY_CELL and isinstance(token, str):
                turn_map = {constants.PLAYER_WHITE: "W", constants.PLAYER_BLACK: "B"}
                current_turn_str = turn_map.get(turn_id)
                if current_turn_str and current_turn_str in token:
                    self.selected_square = (row, col)
        else:
            valid_moves = self.facade.get_valid_moves(self.selected_square[0], self.selected_square[1])
            if (row, col) in valid_moves:
                move_cmd = f"click {self.selected_square[0]} {self.selected_square[1]} {row} {col}"

                self.facade.process_move(move_cmd)

                if self.facade.websocket:
                    asyncio.create_task(self.facade.websocket.send(json.dumps({
                        "type": "MOVE", "room": self.room_id, "data": move_cmd
                    })))
                self.selected_square = None
            else:
                self.selected_square = None

    def on_opponent_move(self, move_cmd):
        """Applies moves received from the remote opponent to the local engine."""
        self.facade.process_move(move_cmd)

    def _load_animations(self):
        """Loads and resizes animation frames for all game pieces."""
        base_path = Path(__file__).resolve().parent.parent / "piece_mine"
        if base_path.exists():
            for folder in base_path.iterdir():
                if folder.is_dir() and (path := folder / "states" / "idle").exists():
                    manager = AnimationManager(path)
                    size = int(self.facade.mapper.cell_size * 0.65)
                    for frame in manager.frames:
                        frame.img = cv2.resize(frame.img, (size, size), interpolation=cv2.INTER_AREA)
                    self.piece_animations[folder.name] = manager

    def set_room_id(self, room_id):
        """Sets the active room ID."""
        self.room_id = room_id

    async def run_async(self):
        """Non-blocking game loop to keep network active."""
        last_time = cv2.getTickCount()
        while True:
            now = cv2.getTickCount()
            delta_ms = int((now - last_time) * 1000 / cv2.getTickFrequency())
            last_time = now
            self.facade._runner.interaction_ctrl.manager.process_time_tick(delta_ms)

            canvas = self.renderer.render(self.board_base.img, self.piece_animations, self.selected_square)
            cv2.imshow("Main Board", canvas)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await asyncio.sleep(0.01)