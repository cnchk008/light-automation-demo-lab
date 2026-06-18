from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import UTC, datetime


PROCESS_IMAGE_FORMAT = "!BBBHHHHH"
PROCESS_IMAGE_SIZE = struct.calcsize(PROCESS_IMAGE_FORMAT)

FAULT_LABELS = {
    0: "none",
    501: "no_part_detected",
    502: "low_confidence",
    503: "camera_offline",
}


@dataclass(frozen=True)
class InspectionProcessImage:
    camera_online: bool
    part_detected: bool
    inspection_passed: bool
    confidence_percent: int
    fault_code: int
    inspection_count: int
    reject_count: int
    average_inspection_ms: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            PROCESS_IMAGE_FORMAT,
            int(self.camera_online),
            int(self.part_detected),
            int(self.inspection_passed),
            self.confidence_percent,
            self.fault_code,
            self.inspection_count,
            self.reject_count,
            self.average_inspection_ms,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "InspectionProcessImage":
        if len(data) < PROCESS_IMAGE_SIZE:
            raise ValueError(
                f"Expected at least {PROCESS_IMAGE_SIZE} bytes, received {len(data)}"
            )

        (
            camera_online,
            part_detected,
            inspection_passed,
            confidence_percent,
            fault_code,
            inspection_count,
            reject_count,
            average_inspection_ms,
        ) = struct.unpack(PROCESS_IMAGE_FORMAT, data[:PROCESS_IMAGE_SIZE])

        return cls(
            camera_online=bool(camera_online),
            part_detected=bool(part_detected),
            inspection_passed=bool(inspection_passed),
            confidence_percent=confidence_percent,
            fault_code=fault_code,
            inspection_count=inspection_count,
            reject_count=reject_count,
            average_inspection_ms=average_inspection_ms,
        )


def process_image_to_payload(
    image: InspectionProcessImage,
    *,
    device_id: str = "vision_camera_01",
    timestamp: str | None = None,
) -> dict:
    return {
        "cell_id": device_id,
        "protocol": "ethernet_ip",
        "device_type": "vision_inspection",
        "timestamp": timestamp or datetime.now(UTC).isoformat(),
        "status": {
            "camera_online": image.camera_online,
            "part_detected": image.part_detected,
            "inspection_passed": image.inspection_passed,
            "confidence_percent": image.confidence_percent,
            "fault_code": image.fault_code,
            "fault_label": FAULT_LABELS.get(image.fault_code, "unknown"),
        },
        "metrics": {
            "inspection_count": image.inspection_count,
            "reject_count": image.reject_count,
            "average_inspection_ms": image.average_inspection_ms,
        },
    }
