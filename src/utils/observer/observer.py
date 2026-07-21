class Subject:
    """Manages subscribers and notifies them of events."""
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """Register a new observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, event, data=None):
        """Notify all registered observers of an event."""
        for observer in self._observers:
            observer.update(event, data)

class Observer:
    """Interface for objects that listen to Subject updates."""
    def update(self, event, data):
        """Process an update event."""
        raise NotImplementedError