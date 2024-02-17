import dbus
import dbus.service
import logging
import uuid
from ant_device_types import ANTDeviceType, ant_to_ble_service_uuid_map  # Ensure this import is correct
from ble_constants import *

class LEAdvertisement(dbus.service.Object):

    # Constructor and other methods remain unchanged...
    def __init__(self, bus, local_name, device_id, device_type_code, advertising_type="peripheral"):
        unique_path_id = uuid.uuid4().hex
        self.path = f"/org/bluez/example/advertisement{unique_path_id}"
        self.bus = bus
        self.advertising_type = advertising_type
        self.local_name = local_name
        self.device_type_code = device_type_code
        logging.debug(f"LEAdvertisement created with local name {local_name} and device type code {device_type_code}")
        self.uuids =  self._get_uuids_for_device_type(device_type_code)
        dbus.service.Object.__init__(self, bus, self.path)
   
    def _get_uuids_for_device_type(self, device_type_code):
    # Log the device type code
        logging.info(f"Attempting to retrieve UUIDs for device type code: {device_type_code}")
        
        # Attempt to retrieve the UUIDs
        uuids = ant_to_ble_service_uuid_map.get(device_type_code, [])
        
        # Log the retrieved UUIDs or a message indicating none were found
        if uuids:
            logging.info(f"UUIDs retrieved for device type code {device_type_code}: {uuids}")
        else:
            logging.info(f"No UUIDs found for device type code {device_type_code}")
        
        return uuids
    
    @dbus.service.method(LE_ADVERTISING_IFACE, in_signature="", out_signature="")
    def Release(self):
        logging.debug("Advertisement Released")

    def get_properties(self):
        logging.debug(self.local_name)
        return {
            LE_ADVERTISING_IFACE: {
                "Type": self.advertising_type,
                "ServiceUUIDs": self.uuids,
                "LocalName": self.local_name,
            }
        }

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface == LE_ADVERTISING_IFACE:
            return self.get_properties()[LE_ADVERTISING_IFACE]
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')
