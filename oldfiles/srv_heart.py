#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later

from BatteryService import BatteryService
from HeartRateService import HeartRateService
from TestService import TestService
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import random

from gi.repository import GLib  # Correct import for GLib
import sys

from ble_advertisement import LEAdvertisement

mainloop = None

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'





class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(HeartRateService(bus, 0))
        self.add_service(BatteryService(bus, 1))
        self.add_service(TestService(bus, 2))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Find the adapter that supports GATT services
    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    app = Application(bus)
    
    # Register GATT application with the GATT Manager
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
    service_manager.RegisterApplication(app.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), "org.bluez.LEAdvertisingManager1")

    # Generate a dynamic name with "Device" prefix and a random five-digit number
    dynamic_name = "Device" + str(random.randint(10000, 99999))
    i = 0
    advertisement = LEAdvertisement(bus, i, local_name=dynamic_name)

    try:
        ad_manager.RegisterAdvertisement(advertisement.path, {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
        print(f"Advertisement {dynamic_name} registered")
    except Exception as e:
        print(f"Failed to register advertisement {dynamic_name}: {e}")

    # Start the GLib Main Loop to process D-Bus events
    mainloop = GLib.MainLoop()
    mainloop.run()

if __name__ == '__main__':
    main()
