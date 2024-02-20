# ant_data_collector.py
import asyncio
import logging
import threading
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
# Import all specific device classes you plan to use
from openant.devices.heart_rate import HeartRate
from openant.devices.fitness_equipment import FitnessEquipment
from openant.devices.power_meter import PowerMeter
from event_system.event_publisher import AsyncEventPublisher
from event_system.observation_utils import start_observation_for_device_type


# Add more imports as needed

def async_to_sync(func):
    """Decorator to run an async function to completion in a new event loop."""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        def run():
            asyncio.set_event_loop(loop)
            loop.run_until_complete(func(*args, **kwargs))
            loop.close()
        thread = threading.Thread(target=run)
        thread.start()
    return wrapper

class ANTDataCollector:
    def __init__(self, device_id, device_type_code, event_publisher: AsyncEventPublisher):
        self.node = Node()
        self.device_id = device_id
        self.device_type_code = device_type_code
        self.device = None  # This will hold the specific ANT+ device instance
        self.event_publisher = event_publisher

    def initialize_device(self):
        # Initialize ANT+ network key
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        # Dynamically select and instantiate the device based on device_type_code
        device_class = self.get_device_class_by_code(self.device_type_code)
        if device_class:
            self.device = device_class(self.node, device_id=self.device_id)
            # Simplify the event binding to just what's necessary for data collection
            self.device.on_device_data = self.on_device_data
        else:
            logging.error(f"Unsupported device type code: {self.device_type_code}")

    def get_device_class_by_code(self, code):
        # Map device_type_code to the corresponding device class
        device_class_map = {
            120: HeartRate,  # Example device type code to class mapping
            17: FitnessEquipment,  # Add mappings for other device types
            11: PowerMeter
            # Add mappings for other device types
        }
        return device_class_map.get(code)

    @async_to_sync
    async def on_device_data(self, page, page_name, data):
        logging.info(f"Data received: Page {page} ({page_name}), Data: {data}")
        await self.event_publisher.notify_observers(data)

    def start_data_collection(self):
        observer_instance = None
        if not self.device:
            self.initialize_device()

        if self.device:
            logging.info(f"Starting data collection for device {self.device_id}")
            try:
                # Dynamically determine and register the corresponding BLE observer
                observer_instance = start_observation_for_device_type(self.device_type_code, self.event_publisher)
                
                if observer_instance:
                    logging.info(f"Registered BLE observer for device {self.device_id}")
                    self.node.start()
                else:
                    logging.error(f"No BLE observer registered for device type code: {self.device_type_code}")
                    
            except Exception as e:
                logging.error(f"Error starting data collection for device {self.device_id}: {e}")
                # Optionally unregister the BLE observer if initialization fails
                if observer_instance:
                    self.event_publisher.remove_observer(observer_instance)
                    logging.info(f"Unregistered BLE observer due to initialization failure for device {self.device_id}")


    def stop_data_collection(self):
        if self.device:
            self.device.close_channel()
        self.node.stop()
        logging.info("Data collection stopped.")

