# ant_scanner.py

from openant.easy.node import Node
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner
from openant.devices import ANTPLUS_NETWORK_KEY
import threading
import logging
import usb.core  # Needed for catching USBError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables for thread control and the ANT+ node instance
scanner_thread = None
scanner = None

node = None  # Declare node globally for access in stop_scanning()

# Callback function placeholder
device_found_callback = None

def set_device_found_callback(callback):
    global device_found_callback
    device_found_callback = callback

def scan_devices(device_id=0, device_type=0, auto_create=False):
    global node, scanner  # Ensure node is accessible globally

    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    scanner = Scanner(node, device_id=device_id, device_type=device_type)
    scanner.on_found = lambda device_tuple: device_found_callback(device_tuple) if device_found_callback else None

    try:
        node.start()
    except KeyboardInterrupt:
        logging.info("Scanner interrupted")
    except usb.core.USBError as e:
        logging.error(f"USB Error encountered: {e}")
    finally:
        logging.info("ANT+ scanner stopped and node closed")

def start_scanning():
    global scanner_thread
    scanner_thread = threading.Thread(target=scan_devices, daemon=True)  # Optionally make it a daemon thread
    scanner_thread.start()

def stop_scanning():
    global node, scanner, scanner_thread
    logging.info("Stopping ANT+ scanning...")

    if scanner:
        try:
            scanner.close_channel()
            logging.info("Scanner channel closed.")
        except Exception as e:
            logging.error(f"Error closing scanner channel: {e}")

    if node:
        try:
            logging.info("Stopping ANT+ node...")
            node.stop()  # This stops the ANT+ node and closes the USB connection
        except Exception as e:
            logging.error(f"Error stopping node: {e}")

    # Wait for the scanner thread to finish only after attempting to stop the node
    if scanner_thread and scanner_thread.is_alive():
        logging.info("Waiting for scanner thread to join...")
        scanner_thread.join()
        logging.info("Scanner thread joined.")

    # Optionally reset the scanner and node to None if you plan to reinitialize them later
    scanner = None
    node = None

            

