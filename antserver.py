from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import emit
from DBusSetup import setup_and_register_application
import threading
import time
import random
from ble_advertising import start_ble_advertising, stop_ble_advertising
import logging

# Basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Assuming you have a global or shared variable to control the polling loop
is_polling = False

@socketio.on('advertise_device')
def handle_advertise_device(json):
    device_id = json.get('device_id')
    logging.info(f'Advertise device requested: {device_id}')
    start_ble_advertising(device_id)  # Start BLE advertising with the given device ID

def scan_for_ant_devices():
    global is_polling
    is_polling = True  # Start polling
    while is_polling:
        # Simulate polling for a device
        time.sleep(1)  # Polling interval
        device_id = random.randint(1, 100)
        
        # Check if we should still be polling
        if not is_polling:
            break
        
        # Simulate finding a device and emit to all connected clients
        logging.info(f"Found ANT+ Device: {device_id}")
        socketio.emit('new_device', {'device_id': device_id})

# Example usage
def start_polling():
    polling_thread = threading.Thread(target=scan_for_ant_devices)
    polling_thread.start()

def stop_polling():
    global is_polling
    is_polling = False

@socketio.on('stop_polling')
def handle_stop_polling(json):
    logging.info('Stop polling requested:', json)
    stop_polling()  # Call the stop_polling function to update the flag

@app.route('/')
def index():
    return render_template('start.html')

@socketio.on('start_scan')
def handle_start_scan(json):
    logging.info('Received request to start scan: ' + str(json))
    start_polling() # Call the start_polling

if __name__ == '__main__':
    setup_and_register_application()  # Register the application with the GATT Manager
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0')
