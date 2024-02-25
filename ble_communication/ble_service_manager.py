#!/usr/bin/env python3
from Services.CyclingPowerService import CyclingPowerService, CyclingPowerBLEUpdater
from Services.BatteryService import BatteryService
from Services.HeartRateService import HeartRateBLEUpdater, HeartRateService
from Services.TestService import TestService
import dbus
import dbus.mainloop.glib
from ble_communication.ble_constants import *
import logging
from ble_communication.le_advertisement_service import LEAdvertisement
from event_system.ble_observer_registry import BLEObserverRegistry

bus = None
adapter = None
service_manager = None
ad_manager = None

class Application(dbus.service.Object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Application, cls).__new__(cls)
            cls._instance.setup(*args, **kwargs)  # Initialize with bus upon first creation
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("Application instance has not been initialized. Call get_instance with bus parameter first.")
        return cls._instance

    def setup(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        
        # Initialize and add services
        self.add_service(HeartRateService(bus, 0))
        logging.info("HeartRateService added")

        self.add_service(BatteryService(bus, 1))
        logging.info("BatteryService added")

        self.add_service(CyclingPowerService(bus, 2))
        logging.info("CyclingPowerService added")

        # Create an instance of HeartRateBLEUpdater and register it as an observer
        BLEObserverRegistry.register(120, HeartRateBLEUpdater(self))  # register heart_rate_updater for heart rate data
        logging.info("HeartRateBLEUpdater registered as observer for device type code 120")

        BLEObserverRegistry.register(11, CyclingPowerBLEUpdater(self)) # Register power_updater for power data
        logging.info("CyclingPowerBLEUpdater registered as observer for device type code 11")

    def add_service(self, service):
        self.services.append(service)

    @classmethod
    def get_instance(cls, bus=None):
        if cls._instance is None:
            if bus is None:
                raise ValueError("Bus parameter is required for the first instantiation")
            cls(bus)  # This implicitly calls __new__, which will call setup
        return cls._instance

    def get_service_by_type(self, service_type):
        for service in self.services:
            if isinstance(service, service_type):
                return service
        return None
    
    """
    org.bluez.GattApplication1 interface implementation
    """
    def get_path(self):
        return dbus.ObjectPath(self.path)

    #def add_service(self, service):
    #    self.services.append(service)

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
    app = Application.get_instance(bus)

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

# Global reference to the current advertisement object
current_advertisement = None

def start_ble_advertising(device_id, device_type_code):
    global current_advertisement, advertisement_counter  # Reference the global variables

    # Ensure any existing advertisement is stopped before starting a new one
    if current_advertisement is not None:
        stop_ble_advertising()

    logging.info(f"Starting BLE advertising for device {device_id}...")
    dynamic_name = f"Device{device_id}"
    
    current_advertisement = LEAdvertisement(get_bus(), dynamic_name, device_id, device_type_code)
    
    try:
        properties = current_advertisement.get_properties()
        logging.info(f"Advertisement properties: {properties}")
        get_ad_manager().RegisterAdvertisement(current_advertisement.path, {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
        logging.info(f"Advertisement {dynamic_name} registered")
    except Exception as e:
        logging.error(f"Failed to register advertisement {dynamic_name}: {e}")

def stop_ble_advertising():
    global current_advertisement  # Reference the global advertisement object

    if current_advertisement is not None:
        logging.info("Stopping BLE advertising...")
        try:
            get_ad_manager().UnregisterAdvertisement(current_advertisement.path)
            logging.info("Advertisement unregistered successfully.")
            current_advertisement = None  # Reset the advertisement reference after stopping
        except Exception as e:
            logging.error(f"Failed to unregister advertisement: {e}")