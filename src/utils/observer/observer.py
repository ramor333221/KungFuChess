class Subject:
    """Manages local observers grouped by event type to eliminate event type if/else checks."""
    def __init__(self):
        self._observers_by_event = {}

    def attach(self, event, observer):
        """Register a new observer for a specific event type."""
        if event not in self._observers_by_event:
            self._observers_by_event[event] = []
        if observer not in self._observers_by_event[event]:
            self._observers_by_event[event].append(observer)

    def notify(self, event, data=None):
        """Notify only the observers registered for this specific event."""
        for observer in self._observers_by_event.get(event, []):
            observer.update(data)

class Observer:
    """Interface for local objects that listen to Subject updates."""
    def update(self, data):
        """Process update data directly without needing event conditionals."""
        raise NotImplementedError