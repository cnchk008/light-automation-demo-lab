import os


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


MODBUS_HOST = os.getenv("MODBUS_HOST", "127.0.0.1")
MODBUS_PORT = _int_env("MODBUS_PORT", 5020)
MODBUS_UNIT_ID = _int_env("MODBUS_UNIT_ID", 1)

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = _int_env("MQTT_PORT", 1883)
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC",
    "factory/light_automation/cobot_cell_01/status",
)

POLL_INTERVAL_SECONDS = _int_env("POLL_INTERVAL_SECONDS", 2)
