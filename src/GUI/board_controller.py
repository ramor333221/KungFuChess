import asyncio
from pathlib import Path
import cv2

from config import constants
from config.constants import ASSETS_PATH
from shared.domain import MoveCommand
from src.GUI.input_handler import InputHandler
from src.GUI.renderer import Renderer
from src.utils.UI.img import Img
from src.utils.input.board_mapper import BoardMapper
from src.utils.logger.logger import setup_logger
from src.utils.observer.observer import Observer

client_logger = setup_logger("ClientLogger", "client_activity.log")


class BoardController(Observer):
    """Manages game GUI, room state, disconnect timers, and server messages (Agnostic of asset folder names)."""

    def __init__(self, facade, board_path: str = None):
        self.facade = facade
        self.player_color = facade.player_color
        self.facade.attach(self)

        self.facade.on_server_message = self.handle_server_message
        self.facade.on_opponent_disconnect = self.handle_opponent_disconnection

        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.board_base = self._load_board_image(board_path)
        board_img = self.board_base.img if hasattr(self.board_base, 'img') else self.board_base
        self.facade.mapper = BoardMapper(board_img)

        self.selected_square = None
        self.room_name = facade.room_name

        self.disconnect_countdown = None
        self._disconnect_timer_ms = 0
        self.win_message = None

        # Renderer handles all asset loading internally
        self.renderer = Renderer(facade, player_color=self.player_color)
        self.piece_animations = self.renderer.piece_animations

        self.input_handler = InputHandler(
            facade=facade,
            renderer=self.renderer,
            on_board_click=self.handle_click
        )

    def update(self, event, data):
        """Handle observer updates from facade/runner."""
        if event == constants.EVENT_MOVE_COMPLETED:
            self.selected_square = None

    def handle_server_message(self, message_data: dict):
        """Handle incoming server messages and update room/player state safely."""
        try:
            msg_type = message_data.get('type')

            if msg_type == constants.MSG_TYPE_ROOM_CREATED:
                self.room_name = message_data.get('room_name')
                self.facade.room_name = self.room_name
                self.player_color = message_data.get('color', constants.COLOR_WHITE)

            elif msg_type == constants.MSG_TYPE_START:
                self.room_name = message_data.get('room_name') or message_data.get('room')
                self.facade.room_name = self.room_name
                self.player_color = message_data.get('color', self.player_color)
                self.renderer.player_color = self.player_color

            elif msg_type == constants.MSG_TYPE_START_VIEWER:
                self.room_name = message_data.get('room_name') or message_data.get('room')
                self.facade.room_name = self.room_name
                self.player_color = constants.COLOR_VIEWER

            elif msg_type == constants.MSG_TYPE_MOVE:
                move_data = message_data.get('data')
                if move_data:
                    if isinstance(move_data, dict):
                        move_command = MoveCommand(**move_data)
                    elif isinstance(move_data, MoveCommand):
                        move_command = move_data
                    else:
                        move_command = None

                    if move_command:
                        client_logger.info(f"Processing remote move: {move_command}")
                        self.facade.process_move(move_command)
        except Exception as e:
            client_logger.error(f"Error handling server message {message_data}: {e}", exc_info=True)

    def handle_opponent_disconnection(self):
        """Initialize disconnect countdown timer when opponent disconnects."""
        if self.disconnect_countdown is None:
            self.disconnect_countdown = constants.DEFAULT_DISCONNECT_COUNTDOWN
            self._disconnect_timer_ms = 0

    def _handle_move_execution(self, row, col):
        """Execute a piece move if valid using a strongly-typed MoveCommand and send over network."""
        valid_moves = self.facade.get_valid_moves(self.selected_square[0], self.selected_square[1])

        if (row, col) in valid_moves:
            move_command = MoveCommand(
                from_row=self.selected_square[0],
                from_col=self.selected_square[1],
                to_row=row,
                to_col=col
            )
            self.facade.process_move(move_command)

            # Fixed: Check network_client directly to safely trigger network transmission
            if self.facade.network_client:
                asyncio.create_task(self.facade.send_move(move_command))

        self.selected_square = None

    def _initialize_window(self):
        """Initialize the OpenCV window and mouse callback handler."""
        window_title = getattr(constants, 'WINDOW_NAME', 'Main Board')
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_title, self.input_handler.handle_event)

    def _load_board_image(self, board_path):
        """Load the chessboard background image using robust path resolution."""
        if board_path:
            path = Path(board_path)
        elif ASSETS_PATH:
            if ASSETS_PATH.is_file():
                path = ASSETS_PATH
            else:
                path = ASSETS_PATH / "board.png"
        else:
            path = self.project_root / "assests" / "board.png"

        if not path.exists():
            alt_path = self.project_root / "assests" / "board.png"
            if alt_path.exists():
                path = alt_path

        return Img().read(path)

    def handle_click(self, row, col):
        """Handle mouse click events on the board squares."""
        if self.disconnect_countdown is not None and self.disconnect_countdown != constants.DISCONNECT_INACTIVE_STATE:
            return

        if self.player_color == constants.COLOR_BLACK:
            row, col = constants.BOARD_MAX_INDEX - row, constants.BOARD_MAX_INDEX - col

        board_matrix = self.facade.get_board_data()
        token = board_matrix[row][col]

        if self.selected_square is None:
            if self._is_player_piece(token):
                self.selected_square = (row, col)
        else:
            self._handle_move_execution(row, col)

    def _is_player_piece(self, token):
        """Verify if the piece token belongs to the current player color."""
        if not token or token == constants.EMPTY_CELL or not isinstance(token, str):
            return False
        if self.player_color == constants.COLOR_WHITE and constants.PIECE_WHITE_INDICATOR in token:
            return True
        if self.player_color == constants.COLOR_BLACK and constants.PIECE_BLACK_INDICATOR in token:
            return True
        return False

    async def start_game_when_matched(self):
        """Wait for match start and initialize game run loop."""
        await self.facade.wait_for_match_and_listen(self._on_match_started)

    async def _on_match_started(self, room_name):
        """Callback executed when match successfully starts."""
        if room_name:
            self.room_name = room_name
            self.facade.room_name = room_name

        self.player_color = self.facade.player_color
        self.renderer.player_color = self.player_color

        self._initialize_window()

        await self.facade.initialize_broker_listeners()
        asyncio.create_task(self.facade.listen_for_server_messages())
        await self.run_async()

    async def run_async(self):
        """Run the main asynchronous game render and event loop with exception safety and zero magic numbers."""
        last_time = cv2.getTickCount()
        window_title = getattr(constants, 'WINDOW_NAME', 'Main Board')
        color_green = getattr(constants, 'COLOR_GREEN_BGR', (0, 255, 0))
        color_red = getattr(constants, 'COLOR_RED_BGR', (0, 0, 255))
        wait_delay = getattr(constants, 'CV_WAIT_KEY_DELAY', 1)

        try:
            while True:
                now = cv2.getTickCount()
                delta_ms = int((now - last_time) * constants.MS_PER_SECOND / cv2.getTickFrequency())
                last_time = now

                if self.disconnect_countdown is not None and self.disconnect_countdown > 0:
                    self._disconnect_timer_ms += delta_ms
                    if self._disconnect_timer_ms >= constants.ONE_SECOND_MS:
                        self._disconnect_timer_ms -= constants.ONE_SECOND_MS
                        self.disconnect_countdown -= 1

                    if self.disconnect_countdown <= 0:
                        self.disconnect_countdown = constants.DISCONNECT_INACTIVE_STATE
                        self.win_message = f"Opponent disconnected! {self.facade.username} wins by default!"
                        self.facade.set_game_winner(self.player_color)

                if self.disconnect_countdown == constants.DISCONNECT_INACTIVE_STATE and self.win_message:
                    canvas = self.renderer.render(self.board_base.img, self.renderer.piece_animations, self.selected_square)
                    img_canvas = canvas.img if hasattr(canvas, 'img') else canvas
                    cv2.putText(
                        img_canvas,
                        self.win_message,
                        (constants.TEXT_OFFSET_X, constants.TEXT_DISCONNECT_Y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        constants.TEXT_FONT_SCALE_MEDIUM,
                        color_green,
                        constants.TEXT_THICKNESS,
                        cv2.LINE_AA
                    )
                    cv2.imshow(window_title, img_canvas)
                    cv2.waitKey(wait_delay)
                    await asyncio.sleep(constants.EXIT_DELAY_SECONDS)
                    break

                self.facade._runner.interaction_ctrl.manager.process_time_tick(delta_ms)
                canvas = self.renderer.render(self.board_base.img, self.renderer.piece_animations, self.selected_square)
                img_canvas = canvas.img if hasattr(canvas, 'img') else canvas

                if self.room_name:
                    cv2.putText(
                        img_canvas,
                        f"Room: {self.room_name}",
                        (constants.TEXT_OFFSET_X, constants.TEXT_ROOM_Y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        constants.TEXT_FONT_SCALE_LARGE,
                        color_green,
                        constants.TEXT_THICKNESS,
                        cv2.LINE_AA
                    )

                if self.disconnect_countdown is not None and self.disconnect_countdown > 0:
                    cv2.putText(
                        img_canvas,
                        f"Opponent disconnected! Resign in: {self.disconnect_countdown}s",
                        (constants.TEXT_OFFSET_X, constants.TEXT_DISCONNECT_Y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        constants.TEXT_FONT_SCALE_MEDIUM,
                        color_red,
                        constants.TEXT_THICKNESS,
                        cv2.LINE_AA
                    )

                cv2.imshow(window_title, img_canvas)

                if cv2.waitKey(wait_delay) & constants.KEY_MASK_8BIT == ord(constants.QUIT_KEY_CHAR):
                    break
                await asyncio.sleep(constants.FRAME_SLEEP_SECONDS)

        except Exception as e:
            client_logger.error(f"Critical error in BoardController run_async loop: {e}", exc_info=True)
            raise
        finally:
            cv2.destroyAllWindows()