import logging
import threading
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from device_communication.ant_scanner import ANTScanner

class ANTDataCollector:
    def __init__(self, device_id, device_type_code):
        self.device_id = device_id
        self.device_type_code = device_type_code
        self.is_connected = False
        self.scanner = ANTScanner(device_id=device_id, device_type=device_type_code)
        self.scanner_thread = None  # Initialize the scanner_thread attribute

    def start_data_collection(self):
        if self.is_connected or (self.scanner_thread and self.scanner_thread.is_alive()):
            logging.info("Data collection is already running.")
            return

        # Define the target function for the thread
        def target_function():
            self.scanner.set_device_found_callback(self.on_device_found)
            self.scanner.set_data_callback(self.on_data_received)
            self.scanner.start_scanning()

        # Start the scanner thread
        self.scanner_thread = threading.Thread(target=target_function, daemon=True)
        self.scanner_thread.start()
        logging.info("Data collection started.")

    def on_data_received(self, data):
        # Handle incoming data from the ANT+ device
        logging.info(f"Data received from ANT+ device: {data}")
        self.forward_data_to_ble(data)

    def on_device_found(self, device_info):
        # Handle device found logic
        self.is_connected = True
        logging.info(f"Device found: {device_info}")

    def stop_data_collection(self):
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner.stop_scanning()
            self.scanner_thread.join()  # Ensure thread completes execution
            self.is_connected = False
            logging.info("Data collection stopped.")


