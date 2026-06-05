import json
import socket

from paho.mqtt import publish

from config import (
    MQTT_HOST,
    MQTT_PORT,
    PROFINET_DEVICE_ID,
    PROFINET_HOST,
    PROFINET_MQTT_TOPIC,
    PROFINET_PORT,
)
from profinet_io import ProfinetProcessImage, process_image_to_payload


def publish_payload(payload: dict) -> None:
    try:
        publish.single(
            PROFINET_MQTT_TOPIC,
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
    bind_address = (PROFINET_HOST, PROFINET_PORT)
    print(
        "Starting gateway: "
        f"Profinet {bind_address[0]}:{bind_address[1]} -> "
        f"MQTT {MQTT_HOST}:{MQTT_PORT}/{PROFINET_MQTT_TOPIC}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(bind_address)

        while True:
            data, sender = sock.recvfrom(1024)
            try:
                image = ProfinetProcessImage.from_bytes(data)
                payload = process_image_to_payload(image, device_id=PROFINET_DEVICE_ID)
                publish_payload(payload)
                print(f"Published from {sender[0]}:{sender[1]}: {json.dumps(payload)}")
            except (ConnectionError, ValueError) as exc:
                print(f"Profinet gateway waiting: {exc}")
            except Exception as exc:
                print(f"Profinet gateway error: {exc}")


if __name__ == "__main__":
    run_gateway()
