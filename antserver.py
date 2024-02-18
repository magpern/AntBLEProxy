from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import emit
from gi.repository import GLib
from ble_communication.ble_service_manager import setup_and_register_application
import threading
import time
import random
from ble_communication.ble_service_manager import start_ble_advertising, stop_ble_advertising
#from device_communication.ant_scanner import start_scanning, stop_scanning, set_device_found_callback  # Import ANT+ scanning functions
import logging
from openant.devices.common import DeviceType
from device_communication.antplus_interface import collect_ant_data
from threading import Thread
from device_communication.ant_scanner import ANTScanner
from device_communication.ant_data_collector import ANTDataCollector

# Basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
ant_scanner = ANTScanner()

def error_notifier(message):
    socketio.emit('error', {'message': message})

def message_notifier(message):
    socketio.emit('message', {'message': message})

ant_scanner.set_error_callback(error_notifier)


# Assuming you have a global or shared variable to control the polling loop
is_polling = False

def device_found_callback(device_tuple):
    device_id, device_type_code, device_trans = device_tuple
    # Convert the device type code to a readable name using the DeviceType enumeration
    try:
        device_type_name = DeviceType(device_type_code).name  # Get the name from the enumeration
    except ValueError:
        # Handle cases where the device_type_code is not recognized
        device_type_name = "Unknown"

    # Now include the readable device type name in the data emitted to the client
    socketio.emit('new_ant_device', {
        'device_id': device_id, 
        'device_type_code': device_type_code,
        'device_type_name': device_type_name,  # Send the readable name
        'transmission_type': device_trans
    })

    logging.info(f"Found ANT+ Device: {device_tuple} as {device_type_name}")

ant_scanner.set_device_found_callback(device_found_callback)

@socketio.on('start_scan')
def handle_start_scan(json):
    socketio.emit('message', {'message': 'Starting ANT+ scan...'})
    ant_scanner.stop_scanning()  # Stop any existing ANT+ scanning
    logging.info('Received request to start ANT+ scan: ' + str(json))
    ant_scanner.start_scanning()
    #threading.Thread(target=ant_scanner.start_scanning).start()  # Start ANT+ scanning in a new thread

@socketio.on('stop_polling')
def handle_stop_scan(json):
    logging.info('Stop ANT+ scanning requested')
    ant_scanner.stop_scanning()  # Stop ANT+ scanning

@socketio.on('advertise_device')
def handle_advertise_device(json):
    socketio.emit('message', {'message': 'Starting BLE advertising...'})
    ant_scanner.stop_scanning()  # Stop any existing ANT+ scanning
    device_id = json.get('device_id')
    device_type_code = json.get('device_type_code')

    logging.info(f'Advertise device requested: Id: {device_id} DeviceType: {device_type_code}')
    start_ble_advertising(device_id, device_type_code)  # Start BLE advertising with the given device ID
    
    # Create an instance of ANTDataCollector for the specified device
    ant_data_collector = ANTDataCollector(device_id, device_type_code)
    
    # Start collecting data from the ANT+ device and forward it to the BLE device in a new thread
    data_thread = Thread(target=ant_data_collector.start_data_collection, daemon=True)
    data_thread.start()

@app.route('/')
def index():
    return render_template('start.html')

@socketio.on('start_data_collection')
def handle_start_data_collection(message):
    device_id = message['device_id']
    device_type_code = message['device_type_code']
    # Convert to appropriate types as necessary
    try:
        device_id = int(device_id)
        device_type_code = int(device_type_code)
        # Start data collection in a separate thread to avoid blocking
        threading.Thread(target=collect_ant_data, args=(device_id, device_type_code)).start()
    except ValueError as e:
        # Handle error, possibly emit error message back to client
        logging.info(f"Error starting data collection: {e}")
    
def run_dbus_loop():
    GLib.MainLoop().run()

if __name__ == '__main__':
    # Initialize and register application with D-Bus
    setup_and_register_application()
    
    # Start the GLib main loop in a separate thread
    dbus_thread = threading.Thread(target=run_dbus_loop)
    dbus_thread.start()

    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0')
