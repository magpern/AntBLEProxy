#!/usr/bin/env python3
from Services.BatteryService import BatteryService
from Services.HeartRateService import HeartRateService
from Services.TestService import TestService
import dbus
import dbus.mainloop.glib
from ble_constants import *
import logging

bus = None
adapter = None
service_manager = None
ad_manager = None

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
        logging.info('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response

def setup_and_register_application():
    global bus, service_manager, ad_manager  # Ensure these are defined globally
    init_dbus()  # Initialize the D-Bus system

    # Create an instance of your application
    app = Application(bus)

    # Register your application with the GATT Manager
    try:
        service_manager.RegisterApplication(app.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
        logging.info("Application registered successfully on D-Bus system.")
    except Exception as e:
        logging.info(f"Failed to register application: {e}")

def init_dbus():
    global bus, adapter, service_manager, ad_manager

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

  # Find the adapter that supports GATT services
    adapter = find_adapter(bus)
    if not adapter:
        logging.info('GattManager1 interface not found')
        return
    
    service_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)

def register_app_cb():
    logging.info('GATT application registered')

def register_app_error_cb(error):
    logging.info('Failed to register application: ' + str(error))
    raise error("Failed to register application: " + str(error))

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None

def get_bus():
    return bus

def get_adapter():
    return adapter

def get_service_manager():
    return service_manager

def get_ad_manager():
    return ad_manager
