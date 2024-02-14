import dbus
import dbus.service

class LEAdvertisement(dbus.service.Object):
    def __init__(self, bus, index, advertising_type="peripheral", local_name="HeartRateMonitor"):
        self.path = f"/org/bluez/example/advertisement{index}"
        self.bus = bus
        self.advertising_type = advertising_type
        self.local_name = local_name  # Add local_name as an attribute
        dbus.service.Object.__init__(self, bus, self.path)
    
    @dbus.service.method("org.bluez.LEAdvertisement1", in_signature="", out_signature="")
    def Release(self):
        print("Advertisement Released")

    def get_properties(self):
        print(self.local_name)
        return {
            "org.bluez.LEAdvertisement1": {
                "Type": self.advertising_type,
                "ServiceUUIDs": ["0000180d-0000-1000-8000-00805f9b34fb"],  # Example: Heart Rate Service
                "LocalName": self.local_name,  # Set the dynamic local name here
            }
        }

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface == "org.bluez.LEAdvertisement1":
            return self.get_properties()["org.bluez.LEAdvertisement1"]
        else:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')
