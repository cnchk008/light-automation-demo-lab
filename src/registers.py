from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class RegisterDefinition:
    address: int
    name: str
    unit: str | None = None


REGISTER_MAP: tuple[RegisterDefinition, ...] = (
    RegisterDefinition(0, "part_present"),
    RegisterDefinition(1, "safety_gate_closed"),
    RegisterDefinition(2, "emergency_stop_ok"),
    RegisterDefinition(3, "robot_busy"),
    RegisterDefinition(4, "fault_code"),
    RegisterDefinition(5, "cycle_count"),
    RegisterDefinition(6, "average_cycle_time_seconds", "s"),
    RegisterDefinition(7, "downtime_seconds", "s"),
)

REGISTER_COUNT = len(REGISTER_MAP)

FAULT_LABELS = {
    0: "none",
    101: "safety_gate_open",
    201: "emergency_stop_not_ok",
}


def registers_to_payload(
    values: list[int] | tuple[int, ...],
    *,
    cell_id: str = "cobot_cell_01",
    timestamp: str | None = None,
) -> dict:
    if len(values) < REGISTER_COUNT:
        raise ValueError(f"Expected {REGISTER_COUNT} registers, received {len(values)}")

    readings = {
        definition.name: values[definition.address]
        for definition in REGISTER_MAP
    }
    fault_code = readings["fault_code"]

    return {
        "cell_id": cell_id,
        "timestamp": timestamp or datetime.now(UTC).isoformat(),
        "status": {
            "part_present": bool(readings["part_present"]),
            "safety_gate_closed": bool(readings["safety_gate_closed"]),
            "emergency_stop_ok": bool(readings["emergency_stop_ok"]),
            "robot_busy": bool(readings["robot_busy"]),
            "fault_code": fault_code,
            "fault_label": FAULT_LABELS.get(fault_code, "unknown"),
        },
        "metrics": {
            "cycle_count": readings["cycle_count"],
            "average_cycle_time_seconds": readings["average_cycle_time_seconds"],
            "downtime_seconds": readings["downtime_seconds"],
        },
    }
