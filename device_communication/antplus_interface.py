# antplus_interface.py
import logging
from openant.easy.node import Node
from openant.easy.channel import Channel

from device_communication.ant_data_collector import ANTDataCollector
from event_system.event_publisher import AsyncEventPublisher
# Import other necessary modules and configurations
collector_registry = {}

def collect_ant_data(device_id, device_type_code, event_publisher: AsyncEventPublisher):
    global collector_registry
    key = (device_id, device_type_code)
    
    logging.info(f"Starting data collection for device {device_id} of type {device_type_code}")
    collector = ANTDataCollector(device_id, device_type_code, event_publisher)
    #store the collector in the registry
    collector_registry[key] = collector
    collector.start_data_collection()
    

def stop_ant_data_collection(device_id, device_type_code):
    global collector_registry
    key = (device_id, device_type_code)
    
    # Retrieve the collector instance
    collector : ANTDataCollector = collector_registry.get(key)
    
    if collector:
        collector.stop_data_collection()
        logging.info(f"Stopped data collection for device {device_id} of type {device_type_code}")
        # Remove the collector from the registry if no longer needed
        del collector_registry[key]
    else:
        logging.error(f"No active data collector found for device {device_id} of type {device_type_code}")

