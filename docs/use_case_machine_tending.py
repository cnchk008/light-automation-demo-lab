USE_CASE = {
    "name": "Cobot machine tending",
    "cell_id": "cobot_cell_01",
    "problem": "Operators spend time loading parts, watching cycle state, and reacting to simple stoppages.",
    "automation_goal": "Expose cell status and downtime signals so a lightweight dashboard or alerting flow can react quickly.",
    "signals": [
        "part_present",
        "safety_gate_closed",
        "emergency_stop_ok",
        "robot_busy",
        "fault_code",
        "cycle_count",
        "average_cycle_time_seconds",
        "downtime_seconds",
    ],
}


if __name__ == "__main__":
    for key, value in USE_CASE.items():
        print(f"{key}: {value}")
