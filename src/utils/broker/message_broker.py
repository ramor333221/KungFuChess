import asyncio
from src.utils.logger.logger import setup_logger

logger = setup_logger("BrokerLogger", "broker_activity.log")

class MessageBroker:
    """Manages asynchronous topic-based message publication and subscription for Pub-Sub."""

    def __init__(self):
        self._subscribers = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, topic: str, callback):
        """Register an asynchronous callback function for a specific pub-sub topic."""
        async with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            if callback not in self._subscribers[topic]:
                self._subscribers[topic].append(callback)

    async def unsubscribe(self, topic: str, callback):
        """Remove a callback function from a specific pub-sub topic."""
        async with self._lock:
            if topic in self._subscribers and callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    async def publish(self, topic: str, message=None):
        """Asynchronously broadcast a message to all subscribers of a topic with error handling."""
        async with self._lock:
            callbacks = list(self._subscribers.get(topic, []))

        for callback in callbacks:
            asyncio.create_task(self._safe_execute_callback(callback, topic, message))

    async def _safe_execute_callback(self, callback, topic, message):
        """Executes a subscriber callback safely, catching and logging any errors."""
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"Error executing callback for topic '{topic}': {e}")