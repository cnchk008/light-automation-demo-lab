from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import UTC, datetime


PROCESS_IMAGE_FORMAT = "!BBHHHHH"
PROCESS_IMAGE_SIZE = struct.calcsize(PROCESS_IMAGE_FORMAT)

FAULT_LABELS = {
    0: "none",
    301: "feeder_jam",
    302: "low_buffer",
    303: "drive_fault",
}


@dataclass(frozen=True)
class ProfinetProcessImage:
    feeder_running: bool
    transfer_ready: bool
    buffer_level_percent: int
    fault_code: int
    feed_count: int
    jam_count: int
    uptime_seconds: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            PROCESS_IMAGE_FORMAT,
            int(self.feeder_running),
            int(self.transfer_ready),
            self.buffer_level_percent,
            self.fault_code,
            self.feed_count,
            self.jam_count,
            self.uptime_seconds,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "ProfinetProcessImage":
        if len(data) < PROCESS_IMAGE_SIZE:
            raise ValueError(
                f"Expected at least {PROCESS_IMAGE_SIZE} bytes, received {len(data)}"
            )

        (
            feeder_running,
            transfer_ready,
            buffer_level_percent,
            fault_code,
            feed_count,
            jam_count,
            uptime_seconds,
        ) = struct.unpack(PROCESS_IMAGE_FORMAT, data[:PROCESS_IMAGE_SIZE])

        return cls(
            feeder_running=bool(feeder_running),
            transfer_ready=bool(transfer_ready),
            buffer_level_percent=buffer_level_percent,
            fault_code=fault_code,
            feed_count=feed_count,
            jam_count=jam_count,
            uptime_seconds=uptime_seconds,
        )


def process_image_to_payload(
    image: ProfinetProcessImage,
    *,
    device_id: str = "profinet_feeder_01",
    timestamp: str | None = None,
) -> dict:
    return {
        "cell_id": device_id,
        "protocol": "profinet",
        "device_type": "part_feeder",
        "timestamp": timestamp or datetime.now(UTC).isoformat(),
        "status": {
            "feeder_running": image.feeder_running,
            "transfer_ready": image.transfer_ready,
            "buffer_level_percent": image.buffer_level_percent,
            "fault_code": image.fault_code,
            "fault_label": FAULT_LABELS.get(image.fault_code, "unknown"),
        },
        "metrics": {
            "feed_count": image.feed_count,
            "jam_count": image.jam_count,
            "uptime_seconds": image.uptime_seconds,
        },
    }
