class BLEObserverRegistry:
    _registry = {}

    @classmethod
    def register(cls, device_type_code, service_instance):
        cls._registry[device_type_code] = service_instance

    @classmethod
    def get_observer(cls, device_type_code):
        return cls._registry.get(device_type_code, None)
