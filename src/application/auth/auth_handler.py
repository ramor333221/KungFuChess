from DB.db_manager import DBManager
from config.constants import DEFAULT_ELO


class AuthHandler:
    """Manages user authentication with automatic registration for new users."""

    def __init__(self):
        self.db = DBManager()

    def login(self):
        """CLI fallback prompt for login with auto-registration."""
        print("--- Chess Login / Register ---")
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        return self.authenticate_or_register(username, password)

    def login_with_credentials(self, username, password):
        """Authenticates user with provided username and password if they exist."""
        if not username:
            return None

        user_data = self.db.get_user_data(username)

        if user_data:
            stored_password, elo = user_data
            if stored_password == password:
                return {"username": username, "elo": elo}
        return None

    def register(self, username, password, elo=DEFAULT_ELO):
        """Registers a new user in the database."""
        if not username:
            return None
        self.db.save_player_record(username, elo, password=password)
        return {"username": username, "elo": elo}

    def authenticate_or_register(self, username, password, default_elo=DEFAULT_ELO):
        """Attempts to log in. If the user does not exist, automatically registers them."""
        if not username:
            return {"username": "Player", "elo": default_elo}

        user_data = self.db.get_user_data(username)

        if user_data:
            stored_password, elo = user_data
            if stored_password == password:
                return {"username": username, "elo": elo}
            else:
                return None
        else:
            try:
                return self.register(username, password, default_elo)
            except Exception:
                return {"username": username, "elo": default_elo}