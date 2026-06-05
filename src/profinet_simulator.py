import random
import socket
import time
from dataclasses import dataclass

from config import (
    PROFINET_CYCLE_TIME_MS,
    PROFINET_GATEWAY_HOST,
    PROFINET_PORT,
)
from profinet_io import ProfinetProcessImage, process_image_to_payload


@dataclass
class FeederState:
    buffer_level_percent: int = 80
    feed_count: int = 0
    jam_count: int = 0
    uptime_seconds: int = 0

    def next_image(self) -> ProfinetProcessImage:
        self.uptime_seconds += max(1, PROFINET_CYCLE_TIME_MS // 1000)
        self.buffer_level_percent = min(
            100,
            max(0, self.buffer_level_percent + random.choice([-3, -2, -1, 0, 4])),
        )

        feeder_running = random.choice([True, True, True, False])
        transfer_ready = feeder_running and self.buffer_level_percent > 5
        fault_code = 0

        if random.randint(1, 28) == 1:
            fault_code = 301
            self.jam_count += 1
            feeder_running = False
            transfer_ready = False
        elif self.buffer_level_percent < 12:
            fault_code = 302
            feeder_running = False
            transfer_ready = False
        elif random.randint(1, 80) == 1:
            fault_code = 303
            feeder_running = False
            transfer_ready = False

        if transfer_ready:
            self.feed_count += 1
            self.buffer_level_percent = max(0, self.buffer_level_percent - 1)

        return ProfinetProcessImage(
            feeder_running=feeder_running,
            transfer_ready=transfer_ready,
            buffer_level_percent=self.buffer_level_percent,
            fault_code=fault_code,
            feed_count=self.feed_count,
            jam_count=self.jam_count,
            uptime_seconds=self.uptime_seconds,
        )


def run_simulator() -> None:
    state = FeederState()
    target = (PROFINET_GATEWAY_HOST, PROFINET_PORT)
    cycle_seconds = PROFINET_CYCLE_TIME_MS / 1000

    print(
        "Starting Profinet cyclic I/O simulator: "
        f"sending process images to {target[0]}:{target[1]}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            image = state.next_image()
            sock.sendto(image.to_bytes(), target)
            payload = process_image_to_payload(image)
            print(f"Profinet process image -> {payload['status']}")
            time.sleep(cycle_seconds)


if __name__ == "__main__":
    run_simulator()
