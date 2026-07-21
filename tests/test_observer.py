import os

from src.application.network.engine_facade import EngineFacade
from src.utils.observer.observer import Observer
from config import constants


class MockObserver(Observer):
    """A test observer that tracks events received."""

    def __init__(self):
        self.events_received = []

    def update(self, event, data):
        """Records the event received for verification."""
        self.events_received.append((event, data))
        print(f"Test: Observer received {event} with data: {data}")


def test_observer_functionality():
    """Verifies that EngineFacade notifies observers upon a move."""
    # 1. Initialize Mock DB and Facade
    # Assuming DBManager is defined elsewhere
    mock_db = None
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    board_path = os.path.join(project_root, "assests", "board.png")

    facade = EngineFacade(board_path=board_path, db_manager=mock_db)

    # 2. Attach Mock Observer
    test_observer = MockObserver()
    facade.attach(test_observer)

    # 3. Trigger a move
    print("Test: Processing move...")
    facade.process_move("click 1 0 2 0")

    # 4. Assert
    if len(test_observer.events_received) > 0:
        event_type, data = test_observer.events_received[0]
        if event_type == constants.EVENT_MOVE_COMPLETED:
            print("SUCCESS: Observer pattern is working correctly!")
        else:
            print("FAILURE: Received incorrect event type.")
    else:
        print("FAILURE: No event received.")


if __name__ == "__main__":
    test_observer_functionality()