import os


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


MODBUS_HOST = os.getenv("MODBUS_HOST", "127.0.0.1")
MODBUS_PORT = _int_env("MODBUS_PORT", 5020)
MODBUS_UNIT_ID = _int_env("MODBUS_UNIT_ID", 1)

PROFINET_HOST = os.getenv("PROFINET_HOST", "127.0.0.1")
PROFINET_GATEWAY_HOST = os.getenv("PROFINET_GATEWAY_HOST", "127.0.0.1")
PROFINET_PORT = _int_env("PROFINET_PORT", 34964)
PROFINET_DEVICE_ID = os.getenv("PROFINET_DEVICE_ID", "profinet_feeder_01")
PROFINET_CYCLE_TIME_MS = _int_env("PROFINET_CYCLE_TIME_MS", 1000)

SAFETY_HOST = os.getenv("SAFETY_HOST", "127.0.0.1")
SAFETY_GATEWAY_HOST = os.getenv("SAFETY_GATEWAY_HOST", "127.0.0.1")
SAFETY_PORT = _int_env("SAFETY_PORT", 34965)
SAFETY_DEVICE_ID = os.getenv("SAFETY_DEVICE_ID", "safety_light_curtain_01")
SAFETY_CYCLE_TIME_MS = _int_env("SAFETY_CYCLE_TIME_MS", 500)

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = _int_env("MQTT_PORT", 1883)
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC",
    "factory/light_automation/cobot_cell_01/status",
)
PROFINET_MQTT_TOPIC = os.getenv(
    "PROFINET_MQTT_TOPIC",
    "factory/light_automation/profinet_feeder_01/status",
)
SAFETY_MQTT_TOPIC = os.getenv(
    "SAFETY_MQTT_TOPIC",
    "factory/light_automation/safety_light_curtain_01/status",
)
MQTT_TOPIC_FILTER = os.getenv("MQTT_TOPIC_FILTER", MQTT_TOPIC)

POLL_INTERVAL_SECONDS = _int_env("POLL_INTERVAL_SECONDS", 2)

DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = _int_env("DASHBOARD_PORT", 8080)
