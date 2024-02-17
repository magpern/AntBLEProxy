# Assuming ad_manager, LEAdvertisement, register_app_cb, and register_app_error_cb are already defined and imported
import logging
from ble_communication.le_advertisement_service import LEAdvertisement
from ble_communication.ble_manager import get_ad_manager, register_app_cb, register_app_error_cb, get_bus

# Global reference to the current advertisement object
current_advertisement = None

def start_ble_advertising(device_id, device_type_code):
    global current_advertisement, advertisement_counter  # Reference the global variables

    # Ensure any existing advertisement is stopped before starting a new one
    if current_advertisement is not None:
        stop_ble_advertising()

    logging.info(f"Starting BLE advertising for device {device_id}...")
    dynamic_name = f"Device{device_id}"
    
    current_advertisement = LEAdvertisement(get_bus(), dynamic_name, device_id, device_type_code)
    
    try:
        properties = current_advertisement.get_properties()
        logging.info(f"Advertisement properties: {properties}")
        get_ad_manager().RegisterAdvertisement(current_advertisement.path, {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
        logging.info(f"Advertisement {dynamic_name} registered")
    except Exception as e:
        logging.error(f"Failed to register advertisement {dynamic_name}: {e}")

def stop_ble_advertising():
    global current_advertisement  # Reference the global advertisement object

    if current_advertisement is not None:
        logging.info("Stopping BLE advertising...")
        try:
            get_ad_manager().UnregisterAdvertisement(current_advertisement.path)
            logging.info("Advertisement unregistered successfully.")
            current_advertisement = None  # Reset the advertisement reference after stopping
        except Exception as e:
            logging.error(f"Failed to unregister advertisement: {e}")