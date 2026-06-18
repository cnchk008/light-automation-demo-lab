import random
import socket
import time
from dataclasses import dataclass

from config import (
    INSPECTION_CYCLE_TIME_MS,
    INSPECTION_GATEWAY_HOST,
    INSPECTION_PORT,
)
from inspection_io import InspectionProcessImage, process_image_to_payload


@dataclass
class VisionInspectionState:
    inspection_count: int = 0
    reject_count: int = 0
    average_inspection_ms: int = 180

    def next_image(self) -> InspectionProcessImage:
        camera_online = random.choice([True, True, True, True, False])
        part_detected = camera_online and random.choice([True, True, True, False])
        confidence_percent = random.randint(72, 99) if part_detected else 0
        inspection_passed = camera_online and part_detected and confidence_percent >= 82
        fault_code = 0

        if not camera_online:
            fault_code = 503
            inspection_passed = False
        elif not part_detected:
            fault_code = 501
        elif confidence_percent < 82:
            fault_code = 502

        if camera_online and part_detected:
            self.inspection_count += 1
            self.average_inspection_ms = random.randint(150, 240)
            if not inspection_passed:
                self.reject_count += 1

        return InspectionProcessImage(
            camera_online=camera_online,
            part_detected=part_detected,
            inspection_passed=inspection_passed,
            confidence_percent=confidence_percent,
            fault_code=fault_code,
            inspection_count=self.inspection_count,
            reject_count=self.reject_count,
            average_inspection_ms=self.average_inspection_ms,
        )


def run_simulator() -> None:
    state = VisionInspectionState()
    target = (INSPECTION_GATEWAY_HOST, INSPECTION_PORT)
    cycle_seconds = INSPECTION_CYCLE_TIME_MS / 1000

    print(
        "Starting vision inspection simulator: "
        f"sending process images to {target[0]}:{target[1]}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            image = state.next_image()
            sock.sendto(image.to_bytes(), target)
            payload = process_image_to_payload(image)
            print(f"Vision inspection image -> {payload['status']}")
            time.sleep(cycle_seconds)


if __name__ == "__main__":
    run_simulator()
