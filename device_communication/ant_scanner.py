import threading
from openant.easy.node import Node
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner
from openant.devices import ANTPLUS_NETWORK_KEY
import logging
import usb.core  # Needed for catching USBError

class ANTScanner:
    def __init__(self, device_id=0, device_type=0, auto_create=False):
        self.node = None
        self.scanner = None
        self.device_id = device_id
        self.device_type = device_type
        self.auto_create = auto_create
        self.device_found_callback = None
        self.scanning_thread = None  # Thread for running the scan

    def set_device_found_callback(self, callback):
        self.device_found_callback = callback

    def set_data_callback(self, callback):
        self.data_callback = callback

    def _scan(self):
        """Internal method to run the scanning process in a thread."""
        logging.info("Starting ANT+ all device scanning...")
        self.node = Node()
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
        self.scanner = Scanner(self.node, device_id=self.device_id, device_type=self.device_type)
        self.scanner.on_found = lambda device_tuple: self.device_found_callback(device_tuple) if self.device_found_callback else None
        self.scanner.on_data = lambda data: self.data_callback(data) if self.data_callback else None

        self.scanner.on_update = lambda device, status: logging.info(f"Received update from device {device}: {status}")
        self.scanner.on_tx_data = lambda device, data: logging.info(f"Received TX data from device {device}: {data}")
        self.scanner.on_battery = lambda device, status: logging.info(f"Received battery status from device {device}: {status}")
        self.scanner.on_device_data = lambda device, data: logging.info(f"Received device data from device {device}: {data}")
        self.scanner.on_ack_data = lambda device, data: logging.info(f"Received ACK data from device {device}: {data}")
        
        logging.info("Starting scanner...")
        try:
            self.node.start()
        except KeyboardInterrupt:
            logging.info("Scanner interrupted")
        except usb.core.USBError as e:
            logging.error(f"USB Error encountered: {e}")
        finally:
            logging.info("ANT+ scanner stopped and node closed")

    def start_scanning(self):
        """Starts the scanning process in a separate thread."""
        if self.scanning_thread and self.scanning_thread.is_alive():
            logging.warning("Scanning is already running.")
            return
        self.scanning_thread = threading.Thread(target=self._scan, daemon=True)
        self.scanning_thread.start()

    def stop_scanning(self):
        """Stops the scanning process and waits for the thread to finish."""
        if self.scanner:
            try:
                self.scanner.close_channel()
                logging.info("Scanner channel closed.")
            except Exception as e:
                logging.error(f"Error closing scanner channel: {e}")

        if self.node:
            try:
                logging.info("Stopping ANT+ node...")
                self.node.stop()
            except Exception as e:
                logging.error(f"Error stopping node: {e}")

        if self.scanning_thread and self.scanning_thread.is_alive():
            logging.info("Waiting for the scanning thread to finish...")
            self.scanning_thread.join()
            logging.info("Scanning thread finished.")
