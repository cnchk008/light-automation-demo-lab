import random
import socket
import time
from dataclasses import dataclass

from config import SAFETY_CYCLE_TIME_MS, SAFETY_GATEWAY_HOST, SAFETY_PORT
from safety_io import SafetyProcessImage, process_image_to_payload


@dataclass
class LightCurtainState:
    interruption_count: int = 0
    last_interruption_ms: int = 0
    reset_latch_cycles: int = 0

    def next_image(self) -> SafetyProcessImage:
        muted = random.choice([False, False, False, True])
        beam_clear = random.choice([True, True, True, True, True, False])
        fault_code = 0

        if not beam_clear and not muted:
            self.interruption_count += 1
            self.last_interruption_ms = random.randint(120, 900)
            self.reset_latch_cycles = random.choice([0, 1, 2, 3])
            fault_code = 401
        elif random.randint(1, 90) == 1:
            self.reset_latch_cycles = random.choice([2, 3, 4])
            fault_code = 403

        reset_required = self.reset_latch_cycles > 0
        if reset_required and fault_code == 0:
            fault_code = 402
            self.reset_latch_cycles -= 1

        ossd_outputs_on = beam_clear and not reset_required and fault_code == 0

        return SafetyProcessImage(
            beam_clear=beam_clear,
            muted=muted,
            reset_required=reset_required,
            ossd_outputs_on=ossd_outputs_on,
            fault_code=fault_code,
            interruption_count=self.interruption_count,
            last_interruption_ms=self.last_interruption_ms,
        )


def run_simulator() -> None:
    state = LightCurtainState()
    target = (SAFETY_GATEWAY_HOST, SAFETY_PORT)
    cycle_seconds = SAFETY_CYCLE_TIME_MS / 1000

    print(
        "Starting safety light curtain simulator: "
        f"sending process images to {target[0]}:{target[1]}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        while True:
            image = state.next_image()
            sock.sendto(image.to_bytes(), target)
            payload = process_image_to_payload(image)
            print(f"Light curtain safety image -> {payload['status']}")
            time.sleep(cycle_seconds)


if __name__ == "__main__":
    run_simulator()
