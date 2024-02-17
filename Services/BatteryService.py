from Services.CharacteristicBase import Characteristic
from Services.ServiceBase import Service
from ble_communication.ble_constants import *
from gi.repository import GLib
import dbus
import dbus.service
import dbus.mainloop.glib

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
        # Update the battery level and notify connected clients if notifying is enabled
        self.battery_lvl = max(0, min(100, level))
        if self.notifying:
            self.notify_battery_level()


class BatteryService(Service):
    BATTERY_UUID = '180f'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))