# Light Automation Demo Lab

A small, runnable demo for a machine-tending light automation cell.

It simulates a Modbus TCP device, reads the cell state through a gateway, converts the register values into JSON, and publishes the result to MQTT.

## What it shows

- A cobot cell simulator exposing eight Modbus holding registers.
- A Modbus-to-MQTT gateway that publishes production status.
- A local Mosquitto broker for testing.
- A subscriber helper that prints the MQTT messages.
- A simple ROI calculator for the automation business case.

## Architecture

```text
Modbus simulator -> Modbus-to-MQTT gateway -> MQTT broker -> subscriber/dashboard
```

The main topic is:

```text
factory/light_automation/cobot_cell_01/status
```

## Run with Docker

```bash
docker compose up --build
```

You should see the simulator updating registers, the gateway publishing JSON, and the subscriber printing messages.

## Run locally

Create or activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start a local MQTT broker. With Docker:

```bash
docker compose up mqtt
```

In separate terminals, run:

```bash
python src/modbus_simulator.py
python src/modbus_to_mqtt_gateway.py
python src/mqtt_subscriber.py
```

## Register Map

| Address | Name | Meaning |
| --- | --- | --- |
| 0 | `part_present` | 1 when a part is waiting in the cell |
| 1 | `safety_gate_closed` | 1 when the safety gate is closed |
| 2 | `emergency_stop_ok` | 1 when the E-stop circuit is healthy |
| 3 | `robot_busy` | 1 when the robot is in cycle |
| 4 | `fault_code` | 0, 101, or 201 |
| 5 | `cycle_count` | completed simulated cycles |
| 6 | `average_cycle_time_seconds` | simulated average cycle time |
| 7 | `downtime_seconds` | accumulated simulated downtime |

## Example Payload

```json
{
  "cell_id": "cobot_cell_01",
  "timestamp": "2026-06-03T09:00:00+00:00",
  "status": {
    "part_present": true,
    "safety_gate_closed": true,
    "emergency_stop_ok": true,
    "robot_busy": true,
    "fault_code": 0,
    "fault_label": "none"
  },
  "metrics": {
    "cycle_count": 42,
    "average_cycle_time_seconds": 11,
    "downtime_seconds": 0
  }
}
```

## Tests

```bash
python -m unittest discover -s tests
```

## ROI Calculator

```bash
python src/roi_calculator.py
```
