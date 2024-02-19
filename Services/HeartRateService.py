from Services.BatteryService import BatteryLevelCharacteristic
from Services.CharacteristicBase import Characteristic
from Services.ServiceBase import Service
from ble_communication.ble_constants import *

class BodySensorLocationChrc(Characteristic):
    BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    def ReadValue(self, options):
        # Return 'Chest' as the sensor location.
        return [0x01]

class HeartRateMeasurementChrc(Characteristic):
    HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        # Start logic to send heart rate measurements.

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        # Stop logic to send heart rate measurements.
    
    def update_heart_rate(self, heart_rate):
        if not self.notifying:
            # If we're not in a notifying state, there's no need to update
            return

        # Heart rate is a uint8, so we make sure it's in the correct range
        heart_rate = max(0, min(255, heart_rate))

        # The first byte of the value has to specify the flags.
        # Here, 0x00 means the format is UINT8 and sensor contact is not supported
        flags = 0x00

        # The second byte is the heart rate measurement itself
        value = [dbus.Byte(flags), dbus.Byte(heart_rate)]

        # Send a notification to connected clients with the new value
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

class HeartRateService(Service):
    HR_UUID = '0000180d-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
        self.add_characteristic(BatteryLevelCharacteristic(bus, 1, self))
        #self.add_characteristic(BodySensorLocationChrc(bus, 1, self))

    def update_heart_rate(self, heart_rate):
        # Find the HeartRateMeasurementChrc characteristic
        for chrc in self.get_characteristics():
            if isinstance(chrc, HeartRateMeasurementChrc):
                # Update heart rate if this is the correct characteristic
                chrc.update_heart_rate(heart_rate)
                break
        else:
            print("HeartRateMeasurementChrc not found.")

