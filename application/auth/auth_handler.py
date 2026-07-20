from DB.db_manager import DBManager


class AuthHandler:
    """Manages CLI-based user authentication."""

    def __init__(self):
        self.db = DBManager()

    def login(self):
        """Prompts the user for credentials via the CLI."""
        print("--- Chess Login ---")
        username = input("Enter Username: ")
        password = input("Enter Password: ")

        user_data = self.db.get_user_data(username)

        if user_data:
            stored_password, elo = user_data
            if stored_password == password:
                print(f"Login successful! Welcome {username}, ELO: {elo}")
                return {"username": username, "elo": elo}
            else:
                print("Incorrect password.")
        else:
            print("User not found.")
        return None