# ble_updater.py within the ble_communication directory
from event_system.observer_interface import AsyncObserverInterface

class AsyncBLEUpdater(AsyncObserverInterface):
    def __init__(self, event_publisher):
        # Register self as an observer
        event_publisher.register_observer(self)

    async def update(self, data):
        # Asynchronously handle the data to update BLE characteristics
        # Example: print data or send it to a BLE device
        print(f"Async updating BLE characteristics with data: {data}")
