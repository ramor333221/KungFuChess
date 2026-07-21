from DB.db_manager import DBManager


class GameManager:
    """Central manager for active sessions and data persistence."""

    def __init__(self):
        self.rooms = {}
        self.db = DBManager()

    def create_room(self, room_id):
        """Initializes a new game room instance."""
        if room_id not in self.rooms:
            # GameRoom initialization will be handled in the next steps
            pass