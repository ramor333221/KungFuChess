import cv2
import asyncio
import json
from pathlib import Path

from src.GUI.input_handler import InputHandler
from src.GUI.renderer import Renderer
from src.utils.UI.animation_manager import AnimationManager
from src.utils.UI.img import Img
from src.utils.logger.logger import setup_logger
from src.utils.observer.observer import Observer
from config import constants

client_logger = setup_logger("ClientLogger", "client_activity.log")


class BoardController(Observer):
    """
    Manages the game board GUI, client-side logs, home screen options,
    room identifiers, and disconnect countdown overlays via OpenCV.
    """

    def __init__(self, facade, board_path: str = None):
        """Initializes the board controller, attaches observers, and sets up initial UI parameters."""
        self.facade = facade
        self.player_color = facade.player_color
        self.facade.attach(self)

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.board_base = self._load_board_image(board_path)

        self.piece_animations = {}
        self.selected_square = None
        self.room_id = None

        # Disconnect countdown states
        self.disconnect_countdown = None
        self.last_countdown_tick = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0

        self.renderer = Renderer(facade, player_color=self.player_color)
        self.input_handler = InputHandler(
            facade=facade,
            renderer=self.renderer,
            on_board_click=self.handle_click
        )

        self._load_animations()
        client_logger.info("BoardController initialized successfully (Window deferred).")

    def show_home_screen(self) -> tuple[str, str]:
        """Displays a simple OpenCV home screen window or text prompt workflow for room actions."""
        client_logger.info("Displaying Home Screen menu.")
        print("\n--- Home Screen ---")
        print("1. Create Room")
        print("2. Join Room")
        print("3. Cancel")

        choice = input("Choose an option (1/2/3): ").strip()
        if choice == '1':
            client_logger.info("User selected: Create Room")
            return "CREATE", ""
        elif choice == '2':
            r_id = input("Enter Room ID to Join: ").strip()
            client_logger.info(f"User selected: Join Room with ID {r_id}")
            return "JOIN", r_id
        else:
            client_logger.info("User selected: Cancel / Exit")
            return "CANCEL", ""

    def update(self, event, data):
        """Processes observer notifications."""
        if event == constants.EVENT_MOVE_COMPLETED:
            client_logger.info(f"Move completed event processed: {data}")

    def handle_server_message(self, message_data: dict):
        """Handles incoming network messages including disconnection timers, remote moves, and status flags."""
        msg_type = message_data.get('type')
        client_logger.info(f"Received server message type: {msg_type}")

        if msg_type == 'ROOM_CREATED':
            self.room_id = message_data.get('room')
            client_logger.info(f"Room assigned (Created): {self.room_id}")
        elif msg_type == 'START':
            self.room_id = message_data.get('room')
            client_logger.info(f"Game started in room {self.room_id} as {self.player_color}")
        elif msg_type == 'MOVE':
            move_data = message_data.get('data')
            if move_data:
                client_logger.info(f"Processing remote move from opponent: {move_data}")
                self.facade.process_move(move_data)
        elif msg_type == 'OPPONENT_DISCONNECTED':
            self.disconnect_countdown = message_data.get('countdown', 20)
            client_logger.warning("Opponent disconnected! Starting local visual countdown.")
        elif msg_type == 'WIN_BY_TIMEOUT':
            client_logger.info("Won game due to opponent timeout.")
            print(message_data.get('message'))
            self.disconnect_countdown = -1

    def _initialize_window(self):
        """Initializes the OpenCV display window and mouse callback handlers."""
        cv2.namedWindow("Main Board", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.input_handler.handle_event)

    def _load_board_image(self, board_path):
        """Loads the board background image from the given path."""
        path = Path(board_path) if board_path else self.project_root / "assests" / "board.png"
        return Img().read(path)

    def handle_click(self, row, col):
        """Handles board cell click events allowing clicking any square to move own pieces freely."""
        if self.player_color == 'black':
            row, col = 7 - row, 7 - col

        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        # אם אין עדיין משבצת נבחרת, נבדוק האם לחיצה זו היא על כלי של השחקן עצמו
        if self.selected_square is None:
            if self._is_player_piece(token):
                self.selected_square = (row, col)
                client_logger.info(f"Piece selected at row {row}, col {col}")
            else:
                client_logger.info(f"Clicked empty or opponent square at row {row}, col {col} (Ignored for selection)")
        else:
            # אם כבר יש כלי נבחר, הלחיצה הזו משמשת כיעד תנועה לכל משבצת שנבחרה (כל עוד חוקית)
            self._handle_move_execution(row, col)

    def _is_player_piece(self, token):
        """Checks if the piece belongs to the current player's color."""
        if not token or token == constants.EMPTY_CELL or not isinstance(token, str):
            return False
        if self.player_color == 'white' and "W" in token:
            return True
        if self.player_color == 'black' and "B" in token:
            return True
        return False

    def _handle_move_execution(self, row, col):
        """Executes a move locally to any target square and transmits it via WebSocket."""
        valid_moves = self.facade.get_valid_moves(self.selected_square[0], self.selected_square[1])

        # בדיקה האם היעד שנבחר נמצא ברשימת המהלכים החוקיים של הכלי
        if (row, col) in valid_moves:
            move_cmd = f"click {self.selected_square[0]} {self.selected_square[1]} {row} {col}"
            self.facade.process_move(move_cmd)
            client_logger.info(f"Executed move command locally: {move_cmd}")

            if self.facade.websocket and self.room_id:
                asyncio.create_task(self.facade.websocket.send(json.dumps({
                    "type": "MOVE", "room": self.room_id, "data": move_cmd
                })))
                client_logger.info("Transmitted move over WebSocket.")
        else:
            client_logger.info(f"Invalid move target attempted: row {row}, col {col}")

        # איפוס הבחירה בכל מקרה לאחר ניסיון תנועה
        self.selected_square = None

    def _load_animations(self):
        """Loads piece animation assets from disk."""
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
        """Starts listening for the match confirmation from the server."""
        await self.facade.wait_for_match_and_listen(self._on_match_started)

    async def _on_match_started(self, room_id):
        """Internal callback executed when the server confirms a match."""
        if room_id:
            self.room_id = room_id

        self.player_color = self.facade.player_color
        self.renderer.player_color = self.player_color

        print("[BoardController] Match confirmed! Initializing GUI window and starting game loop...")

        self._initialize_window()

        asyncio.create_task(self.facade.listen_for_moves(self.handle_server_message))

        await self.run_async()

    def set_room_id(self, room_id):
        """Sets the current room identifier."""
        self.room_id = room_id

    async def run_async(self):
        """Main rendering loop with OpenCV text overlays, countdown ticker, and safe exit handling."""
        last_time = cv2.getTickCount()
        timer_accumulator = 0

        while True:
            if self.disconnect_countdown == -1:
                client_logger.info("Closing window due to game termination.")
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

            if self.room_id:
                cv2.putText(
                    canvas.img if hasattr(canvas, 'img') else canvas,
                    f"Room ID: {self.room_id}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

            if self.disconnect_countdown is not None and self.disconnect_countdown > 0:
                cv2.putText(
                    canvas.img if hasattr(canvas, 'img') else canvas,
                    f"Opponent Disconnected! Auto-resign in: {self.disconnect_countdown}s",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

            cv2.imshow("Main Board", canvas.img if hasattr(canvas, 'img') else canvas)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                client_logger.info("User closed window via 'q' key.")
                break
            await asyncio.sleep(0.01)

        cv2.destroyAllWindows()