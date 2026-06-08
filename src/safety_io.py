from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import UTC, datetime


PROCESS_IMAGE_FORMAT = "!BBBBHHH"
PROCESS_IMAGE_SIZE = struct.calcsize(PROCESS_IMAGE_FORMAT)

FAULT_LABELS = {
    0: "none",
    401: "beam_interrupted",
    402: "manual_reset_required",
    403: "alignment_fault",
}


@dataclass(frozen=True)
class SafetyProcessImage:
    beam_clear: bool
    muted: bool
    reset_required: bool
    ossd_outputs_on: bool
    fault_code: int
    interruption_count: int
    last_interruption_ms: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            PROCESS_IMAGE_FORMAT,
            int(self.beam_clear),
            int(self.muted),
            int(self.reset_required),
            int(self.ossd_outputs_on),
            self.fault_code,
            self.interruption_count,
            self.last_interruption_ms,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SafetyProcessImage":
        if len(data) < PROCESS_IMAGE_SIZE:
            raise ValueError(
                f"Expected at least {PROCESS_IMAGE_SIZE} bytes, received {len(data)}"
            )

        (
            beam_clear,
            muted,
            reset_required,
            ossd_outputs_on,
            fault_code,
            interruption_count,
            last_interruption_ms,
        ) = struct.unpack(PROCESS_IMAGE_FORMAT, data[:PROCESS_IMAGE_SIZE])

        return cls(
            beam_clear=bool(beam_clear),
            muted=bool(muted),
            reset_required=bool(reset_required),
            ossd_outputs_on=bool(ossd_outputs_on),
            fault_code=fault_code,
            interruption_count=interruption_count,
            last_interruption_ms=last_interruption_ms,
        )


def process_image_to_payload(
    image: SafetyProcessImage,
    *,
    device_id: str = "safety_light_curtain_01",
    timestamp: str | None = None,
) -> dict:
    return {
        "cell_id": device_id,
        "protocol": "profinet_safety",
        "device_type": "light_curtain",
        "timestamp": timestamp or datetime.now(UTC).isoformat(),
        "status": {
            "beam_clear": image.beam_clear,
            "muted": image.muted,
            "reset_required": image.reset_required,
            "ossd_outputs_on": image.ossd_outputs_on,
            "fault_code": image.fault_code,
            "fault_label": FAULT_LABELS.get(image.fault_code, "unknown"),
        },
        "metrics": {
            "interruption_count": image.interruption_count,
            "last_interruption_ms": image.last_interruption_ms,
        },
    }
