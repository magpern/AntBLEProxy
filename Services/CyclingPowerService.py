#CyclingPowerService.py
from Services.CharacteristicBase import Characteristic
from Services.ServiceBase import Service
from ble_communication.ble_constants import *
from event_system.observer_interface import AsyncObserverInterface
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
import logging

class SensorLocationCharacteristic(Characteristic):
    SENSOR_LOCATION_UUID = '00002a5d-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.SENSOR_LOCATION_UUID,
            ['read'],
            service)
        self.sensor_location = 0  # Default to "Other" location

    def ReadValue(self, options):
        # Return 'Other' as the sensor location.
        logging.info(f"SensorLocationCharacteristic: Reading sensor location")
        return [0x0D]
    
class CyclingPowerMeasurementChrc(Characteristic):
    CP_MSRMT_UUID = '00002a63-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CP_MSRMT_UUID,
            ['notify'],
            service)
        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return
        self.notifying = True
        # Here, implement logic to collect and send cycling power measurements

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return
        self.notifying = False
        # Here, implement logic to stop sending cycling power measurements

    def update_cycling_power_measurement(self, measurement_data):
        logging.info(f"CyclingPowerMeasurementChrc: Updating power measurement {measurement_data}")
        if not self.notifying:
            return
        
        power = measurement_data  # Assuming a value for power similar to revolutions and timestamp
        revolutions = 0
        timestamp = 0
        flags = 0x20
        sensor_location = 0x0D  # Assuming you might need to include this as well

        ble_buffer = [0] * 8  # Initialize a list with 8 elements
        ble_buffer[0] = flags & 0xff
        ble_buffer[1] = (flags >> 8) & 0xff
        ble_buffer[2] = power & 0xff
        ble_buffer[3] = (power >> 8) & 0xff
        ble_buffer[4] = revolutions & 0xff
        ble_buffer[5] = (revolutions >> 8) & 0xff
        ble_buffer[6] = timestamp & 0xff
        ble_buffer[7] = (timestamp >> 8) & 0xff

        # If you need to work with bytes directly, consider converting ble_buffer to a bytes object
        ble_bytes = bytes(ble_buffer)
        hex_str = ' '.join(f'{byte:02x}' for byte in ble_bytes)
        logging.info(hex_str)

        # The first byte of the value has to specify the flags.
        # Here, 0x00 means the format is UINT8 and sensor contact is not supported
        flags = 0x00

        # The second byte is the heart rate measurement itself
        value = [dbus.Byte(flags), dbus.Byte(measurement_data)]

        # Send a notification to connected clients with the new value
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': ble_buffer}, [])

class CyclingPowerFeatureChrc(Characteristic):
    CP_FEATURE_UUID = '00002a65-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service, features):
        Characteristic.__init__(
            self, bus, index,
            self.CP_FEATURE_UUID,
            ['read'],
            service)
        self.features = features

    def ReadValue(self, options):
        logging.info(f"CyclingPowerFeatureChrc: Reading features")
        logging.info(f"CyclingPowerFeatureChrc: Reading features {options}")

        # Convert the features into a byte array. The features variable is a bitmask.
        # For simplicity, the actual conversion is not shown here.
        value = []  # This should be populated based on the features supported
        return self.features

class CyclingPowerService(Service):
    CP_UUID = '00001818-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.CP_UUID, True)
        
        fBuffer = [0] * 4
        fBuffer[0] = 0x00
        fBuffer[1] = 0x00
        fBuffer[2] = 0x00
        fBuffer[3] = 0x08

        self.add_characteristic(CyclingPowerFeatureChrc(bus, 1, self, features=bytes(fBuffer)))  # Example feature
        self.add_characteristic(CyclingPowerMeasurementChrc(bus, 0, self))
        self.add_characteristic(SensorLocationCharacteristic(bus, 2, self))

    def update_power(self, power):
        # Find the CyclingPowerMeasurementChrc characteristic
        for chrc in self.get_characteristics():
            if isinstance(chrc, CyclingPowerMeasurementChrc):
                # Update value if this is the correct characteristic
                chrc.update_cycling_power_measurement(power)
                break
        else:
            print("characteristic not found.")

class CyclingPowerBLEUpdater(AsyncObserverInterface):
    def __init__(self, application):
        self.application = application

    async def update(self, data_tuple):
        # Unpack the tuple to get page, page_name, and data
        page, page_name, data = data_tuple
        logging.info(f"CyclingPowerBLEUpdater: Data received: Page {page}, Page Name {page_name}, Data: {data}")

        if page_name == "standard_power":
            _service : CyclingPowerService = self.application.get_service_by_type(CyclingPowerService)
            if _service:
                _service.update_power(data.instantaneous_power)
                #heart_rate_service.update_battery_level(data.last_battery_level)

    async def stop(self):
        logging.info("CyclingPowerBLEUpdater: Stopping data handling.")
        pass