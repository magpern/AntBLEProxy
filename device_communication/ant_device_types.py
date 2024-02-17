from enum import Enum, unique

@unique
class ANTDeviceType(Enum):
    FITNESS_EQUIPMENT = 17
    CYCLING_POWER = 11
    HEART_RATE_MONITOR = 120
    RUNNING_SPEED_AND_CADENCE = 124

# Example usage in the UUID mapping
ant_to_ble_service_uuid_map = {
    ANTDeviceType.FITNESS_EQUIPMENT.value: [
        "00001826-0000-1000-8000-00805f9b34fb",  # Fitness Machine Service UUID
        "00001818-0000-1000-8000-00805f9b34fb"   # Cycling Power Service UUID
    ],
    ANTDeviceType.CYCLING_POWER.value: [
        "00001818-0000-1000-8000-00805f9b34fb",  # Cycling Power Service UUID
        "00001816-0000-1000-8000-00805f9b34fb"   # Cycling Speed and Cadence UUID
    ],
    ANTDeviceType.HEART_RATE_MONITOR.value: [
        "0000180d-0000-1000-8000-00805f9b34fb",  # Heart Rate Service UUID
        "0000180f-0000-1000-8000-00805f9b34fb"   # Battery Service UUID
    ],
    ANTDeviceType.RUNNING_SPEED_AND_CADENCE.value: [
        "00001814-0000-1000-8000-00805f9b34fb"   # Running Speed and Cadence Service UUID
    ]
}
