import json
import socket
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
    try:
        publish.single(
            MQTT_TOPIC,
            payload=json.dumps(payload, separators=(",", ":")),
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            qos=1,
        )
    except OSError as exc:
        raise ConnectionError(
            f"MQTT not reachable at {MQTT_HOST}:{MQTT_PORT}: {exc}"
        ) from exc


def run_gateway() -> None:
    print(
        "Starting gateway: "
        f"Modbus {MODBUS_HOST}:{MODBUS_PORT} -> MQTT {MQTT_HOST}:{MQTT_PORT}/{MQTT_TOPIC}"
    )

    while True:
        client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT, timeout=3)
        try:
            if not client.connect():
                raise ConnectionError(
                    f"Modbus not reachable at {MODBUS_HOST}:{MODBUS_PORT}"
                )

            registers = read_registers(client)
            payload = registers_to_payload(registers)
            publish_payload(payload)
            print(f"Published: {json.dumps(payload)}")
        except (ConnectionError, socket.error) as exc:
            print(f"Gateway waiting: {exc}")
        except Exception as exc:
            print(f"Gateway error: {exc}")
        finally:
            client.close()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_gateway()
