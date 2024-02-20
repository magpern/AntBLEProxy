# observer_interface.py

class AsyncObserverInterface:
    async def update(self, data):
        pass  # Implement in subclasses
    async def stop(self):
        pass
