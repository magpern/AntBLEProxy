import logging
from device_communication.ant_scanner import ANTScanner

class ANTDataCollector:
    def __init__(self, device_id, device_type_code):
        self.device_id = device_id
        self.device_type_code = device_type_code
        self.is_connected = False
        self.scanner = ANTScanner(device_id=device_id, device_type=device_type_code)
        self.scanner.set_device_found_callback(self.on_device_found)
        self.scanner.set_data_callback(self.on_data_received)  # Assuming ANTScanner has this method

    def on_device_found(self, device_info):
        # Logic when a specific device is found. Initiate connection or start data collection
        logging.info(f"Connected to device: {device_info}")
        self.is_connected = True

    def on_data_received(self, data):
        # Handle incoming data from the ANT+ device
        logging.info(f"Data received from ANT+ device: {data}")
        self.forward_data_to_ble(data)

    def start_data_collection(self):
        # Start scanning for the specific device and collect data
        if not self.is_connected:
            self.scanner.start_scanning()

    def forward_data_to_ble(self, data):
        # Logic to forward collected data to the BLE device
        logging.info(f"Forwarding data to BLE: {data}")

    def stop_data_collection(self):
        # Stop the data collection process
        self.scanner.stop_scanning()
        self.is_connected = False
