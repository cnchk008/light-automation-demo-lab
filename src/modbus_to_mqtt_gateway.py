import json
import time

from paho.mqtt import publish
from pymodbus.client import ModbusTcpClient

from config import (
    MODBUS_HOST,
    MODBUS_PORT,
    MODBUS_UNIT_ID,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_TOPIC,
    POLL_INTERVAL_SECONDS,
)
from registers import REGISTER_COUNT, registers_to_payload


def read_registers(client: ModbusTcpClient) -> list[int]:
    result = client.read_holding_registers(
        0,
        count=REGISTER_COUNT,
        device_id=MODBUS_UNIT_ID,
    )

    if result.isError():
        raise RuntimeError(f"Modbus read failed: {result}")

    return list(result.registers)


def publish_payload(payload: dict) -> None:
    publish.single(
        MQTT_TOPIC,
        payload=json.dumps(payload, separators=(",", ":")),
        hostname=MQTT_HOST,
        port=MQTT_PORT,
        qos=1,
    )


def run_gateway() -> None:
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT, timeout=3)
    print(
        "Starting gateway: "
        f"Modbus {MODBUS_HOST}:{MODBUS_PORT} -> MQTT {MQTT_HOST}:{MQTT_PORT}/{MQTT_TOPIC}"
    )

    while True:
        try:
            if not client.connect():
                raise ConnectionError("Could not connect to Modbus simulator")

            registers = read_registers(client)
            payload = registers_to_payload(registers)
            publish_payload(payload)
            print(f"Published: {json.dumps(payload)}")
        except Exception as exc:
            print(f"Gateway waiting: {exc}")
        finally:
            client.close()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_gateway()
