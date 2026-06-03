import os
import socket


def check_tcp(host: str, port: int, timeout: float = 2.0) -> None:
    if host == "0.0.0.0":
        host = "127.0.0.1"
    with socket.create_connection((host, port), timeout=timeout):
        return


if __name__ == "__main__":
    service = os.getenv("HEALTHCHECK_SERVICE", "mqtt")

    if service == "modbus":
        check_tcp(
            os.getenv("MODBUS_HOST", "127.0.0.1"),
            int(os.getenv("MODBUS_PORT", "5020")),
        )
    else:
        check_tcp(
            os.getenv("MQTT_HOST", "127.0.0.1"),
            int(os.getenv("MQTT_PORT", "1883")),
        )
