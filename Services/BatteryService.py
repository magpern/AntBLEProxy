from Services.CharacteristicBase import Characteristic
from Services.ServiceBase import Service
from ble_communication.ble_constants import *
from event_system.observer_interface import AsyncObserverInterface
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib
import logging
class BatteryLevelCharacteristic(Characteristic):
    BATTERY_LVL_UUID = '2a19'

    def __init__(self, bus, index, service, initial_battery_level=100):
        Characteristic.__init__(
                self, bus, index,
                self.BATTERY_LVL_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        self.battery_lvl = initial_battery_level

    def notify_battery_level(self):
        if self.notifying:
            self.PropertiesChanged(
                    GATT_CHRC_IFACE,
                    {'Value': [dbus.Byte(self.battery_lvl)]}, [])

    def ReadValue(self, options):
        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False

    def SetBatteryLevel(self, level):
        if level is None:
            # Handle the None case, e.g., log a warning and return early
            logging.warn("Warning: Attempted to set battery level to None")
            return

        # Proceed with updating the battery level as normal if level is not None
        self.battery_lvl = max(0, min(100, level))
        if self.notifying:
            self.notify_battery_level()


class BatteryService(Service):
    BATTERY_UUID = '180f'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))

    def update_heart_rate(self, heart_rate):
        # Find the HeartRateMeasurementChrc characteristic
        for chrc in self.get_characteristics():
            if isinstance(chrc, BatteryLevelCharacteristic):
                # Update heart rate if this is the correct characteristic
                chrc.SetBatteryLevel(heart_rate)
                break
        else:
            print("HeartRateMeasurementChrc not found.")

class BatteryBLEUpdater(AsyncObserverInterface):
    def __init__(self, application):
        self.application = application

    async def update(self, data_tuple):
        page, page_name, data = data_tuple

        if page_name == 'battery_status':
            pass
  
    async def stop(self):
        logging.info("HeartRateBLEUpdater: Stopping data handling.")
        pass
        