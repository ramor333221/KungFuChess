from config import constants
from shared.domain import MoveCommand
from src.utils.logger.logger import setup_logger

coordinator_logger = setup_logger("CoordinatorLogger", "client_activity.log")


class GameEventCoordinator:
    """Manages network communication and server message routing using dictionary dispatch (zero if/else)."""

    def __init__(self, facade, board_controller):
        self.facade = facade
        self.board_controller = board_controller

        # Bind network handlers to facade
        self.facade.on_server_message = self.handle_server_message
        self.facade.on_opponent_disconnect = self.handle_opponent_disconnection

        # Map message types directly to dedicated handler methods
        self._message_dispatch = {
            constants.MSG_TYPE_ROOM_CREATED: self._handle_room_created,
            constants.MSG_TYPE_START: self._handle_start,
            constants.MSG_TYPE_START_VIEWER: self._handle_start_viewer,
            constants.MSG_TYPE_MOVE: self._handle_move,
        }

    def handle_server_message(self, message_data: dict):
        """Route incoming server messages dynamically via dictionary lookup."""
        try:
            msg_type = message_data.get('type')
            handler = self._message_dispatch.get(msg_type)
            if handler:
                handler(message_data)
        except Exception as e:
            coordinator_logger.error(f"Error handling server message {message_data}: {e}", exc_info=True)

    def _handle_room_created(self, message_data: dict):
        """Handle room creation event."""
        self.board_controller.room_name = message_data.get('room_name')
        self.facade.room_name = self.board_controller.room_name
        self.board_controller.player_color = message_data.get('color', constants.COLOR_WHITE)

    def _handle_start(self, message_data: dict):
        """Handle game start event for players."""
        self.board_controller.room_name = message_data.get('room_name') or message_data.get('room')
        self.facade.room_name = self.board_controller.room_name
        self.board_controller.player_color = message_data.get('color', self.board_controller.player_color)
        self.board_controller.renderer.player_color = self.board_controller.player_color

    def _handle_start_viewer(self, message_data: dict):
        """Handle game start event for spectators."""
        self.board_controller.room_name = message_data.get('room_name') or message_data.get('room')
        self.facade.room_name = self.board_controller.room_name
        self.board_controller.player_color = constants.COLOR_VIEWER

    def _handle_move(self, message_data: dict):
        """Handle incoming remote move payload."""
        move_data = message_data.get('data')
        if move_data:
            move_command = MoveCommand(**move_data) if isinstance(move_data, dict) else move_data
            if move_command:
                coordinator_logger.info(f"Processing remote move: {move_command}")
                self.facade.process_move(move_command)

    def handle_opponent_disconnection(self):
        """Initialize disconnect countdown timer when opponent disconnects."""
        if self.board_controller.disconnect_countdown is None:
            self.board_controller.disconnect_countdown = constants.DEFAULT_DISCONNECT_COUNTDOWN
            self.board_controller._disconnect_timer_ms = 0