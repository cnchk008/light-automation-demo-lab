import json

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT, MQTT_TOPIC_FILTER


def make_client() -> mqtt.Client:
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    return mqtt.Client()


def on_connect(client, userdata, flags, reason_code, properties=None) -> None:
    print(f"Connected to MQTT broker with result {reason_code}")
    client.subscribe(MQTT_TOPIC_FILTER)


def on_message(client, userdata, message) -> None:
    payload = message.payload.decode("utf-8")
    try:
        payload = json.dumps(json.loads(payload), indent=2)
    except json.JSONDecodeError:
        pass
    print(f"\nTopic: {message.topic}\n{payload}")


def run_subscriber() -> None:
    client = make_client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Listening on mqtt://{MQTT_HOST}:{MQTT_PORT}/{MQTT_TOPIC_FILTER}")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    run_subscriber()
