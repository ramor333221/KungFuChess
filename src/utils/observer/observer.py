class Subject:
    """Manages local observers and notifies them of synchronous state changes."""
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        """Register a new observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, event, data=None):
        """Notify all registered local observers about an event."""
        for observer in self._observers:
            observer.update(event, data)

class Observer:
    """Interface for local objects that listen to Subject updates."""
    def update(self, event, data):
        """Process a local update event."""
        raise NotImplementedError