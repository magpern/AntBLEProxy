import logging
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
# Import all specific device classes you plan to use
from openant.devices.heart_rate import HeartRate
from openant.devices.fitness_equipment import FitnessEquipment
from openant.devices.power_meter import PowerMeter

# Add more imports as needed

class ANTDataCollector:
    def __init__(self, device_id, device_type_code):
        self.node = Node()
        self.device_id = device_id
        self.device_type_code = device_type_code
        self.device = None  # This will hold the specific ANT+ device instance

    def initialize_device(self):
        # Initialize ANT+ network key
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        # Dynamically select and instantiate the device based on device_type_code
        device_class = self.get_device_class_by_code(self.device_type_code)
        if device_class:
            self.device = device_class(self.node, device_id=self.device_id)
            self.device.on_device_data = self.on_device_data
            self.device.on_battery = lambda status: logging.info(f"Received battery status: {status}")           
            # Add more event bindings as necessary
        else:
            logging.error(f"Unsupported device type code: {self.device_type_code}")
            return

    def get_device_class_by_code(self, code):
        # Map device_type_code to the corresponding device class
        device_class_map = {
            120: HeartRate,  # Example device type code to class mapping
            17: FitnessEquipment,  # Add mappings for other device types
            11: PowerMeter
            # Add mappings for other device types
        }
        return device_class_map.get(code)

    def on_device_data(self, page, page_name, data):
        # Handle device data and forward to BLE
        logging.info(f"Data received: Page {page} ({page_name}), Data: {data}")
        # Implement data forwarding logic here

    def start_data_collection(self):
        if not self.device:
            self.initialize_device()

        if self.device:
            logging.info(f"Starting data collection for device {self.device_id}")
            try:
                self.node.start()
            except Exception as e:
                logging.error(f"Error starting data collection: {e}")

    def stop_data_collection(self):
        if self.device:
            self.device.close_channel()
        self.node.stop()
        logging.info("Data collection stopped.")

