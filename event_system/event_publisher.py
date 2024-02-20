# event_publisher.py
import asyncio
import logging

class AsyncEventPublisher:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        """Register an observer to receive events."""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from the list."""
        self._observers.remove(observer)

    async def notify_observers(self, data):
        """Notify all registered observers about an event."""
        logging.info(f"I am here Notifying observers about the event")
        # Creating a list of coroutines for each observer's update method
        tasks = [observer.update(data) for observer in self._observers]
        # Wait for all observers to process the event
        await asyncio.gather(*tasks)

    async def notify_observers_stop(self):
        tasks = [observer.stop() for observer in self._observers if hasattr(observer, 'stop')]
        await asyncio.gather(*tasks)
