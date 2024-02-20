#observation_utils.py
import logging
from event_system.ble_observer_registry import BLEObserverRegistry


def start_observation_for_device_type(device_type_code, event_publisher):
    """
    Retrieves and registers the corresponding BLE observer instance
    based on the device type code with the event publisher.
    """
    logging.info(f"Retrieving observer instance for device type code: {device_type_code}")
    observer_instance = BLEObserverRegistry.get_observer(device_type_code)

    if observer_instance:
        # Directly register the observer instance with the event publisher
        event_publisher.register_observer(observer_instance)
        
        logging.info(f"Observer for device type code {device_type_code} registered successfully.")
        return observer_instance
    else:
        logging.error(f"No observer found for device type code: {device_type_code}")
        return None
