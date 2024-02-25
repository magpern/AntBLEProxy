# ant_data_collector.py
import asyncio
import logging
import threading
import time
from openant.easy.node import Node
from openant.devices.common import AntPlusDevice
from openant.devices import ANTPLUS_NETWORK_KEY
# Import all specific device classes you plan to use
from openant.devices.heart_rate import HeartRate
from openant.devices.fitness_equipment import FitnessEquipment
from openant.devices.power_meter import PowerMeter
from event_system.event_publisher import AsyncEventPublisher
from event_system.observation_utils import start_observation_for_device_type, get_observer_instance
import usb.core

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
        self.device : AntPlusDevice = None  # This will hold the specific ANT+ device instance
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

            if self.device:
                original_on_battery = self.device.on_battery

                def on_battery_hook(battery_data):
                    # Log the battery data
                    logging.info(f"Device {self.device_id} Received battery status: {battery_data}")
                    # Forward battery data to observers
                    battery_status = {
                        'battery_id': battery_data.battery_id,
                        'voltage_fractional': battery_data.voltage_fractional,
                        'voltage_coarse': battery_data.voltage_coarse,
                        'status': battery_data.status.value,  # Assuming .status is an enum with a .value attribute
                        'operating_time': battery_data.operating_time,
                    }
                    # Create a tuple for the page, page_name, and data
                    data_tuple = (None, 'battery_status', battery_status)
                    # Ensure you have a reference to the correct event loop for thread-safe coroutine execution
                    if hasattr(self, 'loop') and self.loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            self.event_publisher.notify_observers(data_tuple),
                            self.loop
                        )
                    else:
                        logging.error("Event loop not available or not running in ANTDataCollector")
                    # Call the original on_battery handler, if any
                    if original_on_battery:
                        original_on_battery(battery_data)

                self.device.on_battery = on_battery_hook
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
        # Create a tuple that encapsulates page, page_name, and data
        data_tuple = (page, page_name, data)
        await self.event_publisher.notify_observers(data_tuple)


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
                    time.sleep(0.1)  # Allow time for the node to stop
                    logging.info("ANT+ node exited.")
                else:
                    logging.error(f"No BLE observer registered for device type code: {self.device_type_code}")
                    
            except Exception as e:
                logging.error(f"Error starting data collection for device {self.device_id}: {e}")
                # Optionally unregister the BLE observer if initialization fails
                #if observer_instance:
                    #self.event_publisher.remove_observer(observer_instance)
                    #logging.info(f"Unregistered BLE observer due to initialization failure for device {self.device_id}")

    @async_to_sync
    async def stop_data_collection(self):
        try:
            if self.device:
                logging.info(f"Stopping data collection for device {self.device_id}")
                try:
                    # Attempt to close the channel, with error handling for state issues
                    self.device.close_channel()
                except Exception as e:
                    logging.error(f"Exception closing channel for device {self.device_id}: {e}")
        except Exception as e:
            logging.error(f"Error stopping data collection for device {self.device_id}: {e}")

        try:
            if self.node:
                # Attempt to stop the ANT+ node, with error handling for USB issues
                logging.info("Stopping ANT+ node...")
                self.node.stop()
        except usb.core.USBError as e:
            if e.errno == 2:  # Entity not found
                logging.warning(f"USB device already detached or not found: {e}")
            else:
                logging.error(f"USBError stopping ANT+ node: {e}")
        except Exception as e:
            logging.error(f"Exception stopping ANT+ node: {e}")

        observer_instance = get_observer_instance(self.device_type_code)
        if observer_instance:
            logging.info(f"Stopping BLE observer for device {self.device_id}")
            await self.event_publisher.notify_observers_stop()
            self.event_publisher.remove_observer(observer_instance)
        else:
            logging.error(f"No BLE observer found for device type code: {self.device_type_code}")

        logging.info("Data collection stopped.")


