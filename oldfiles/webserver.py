# webserver.py
from flask import Flask, render_template, request, redirect, url_for
from advertise_service import advertise_ble_device
import random

app = Flask(__name__)

# Generate mock-up ANT+ device IDs
devices = [f"ANT+_{random.randint(1000, 9999)}" for _ in range(5)]

@app.route('/')
def index():
    return render_template('index.html', devices=devices)

@app.route('/advertise', methods=['POST'])
def advertise():
    device_id = request.form.get('device_id')
    if device_id:
        advertise_ble_device(device_id)
        return redirect(url_for('index'))
    return "Error: No device selected", 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
