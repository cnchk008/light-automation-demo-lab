# Light Automation Demo Lab

A small, runnable demo for a machine-tending light automation cell.

It simulates a Modbus TCP device, reads the cell state through a gateway, converts the register values into JSON, and publishes the result to MQTT.

## What it shows

- A cobot cell simulator exposing eight Modbus holding registers.
- A Modbus-to-MQTT gateway that publishes production status.
- A local Mosquitto broker for testing.
- A subscriber helper that prints the MQTT messages.
- A browser dashboard for live cell visualization.
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

The MQTT broker runs on port `1883` inside Docker and is exposed on your Mac as `1884` to avoid conflicts with any existing local MQTT broker.

Open the live dashboard at:

```text
http://localhost:8080
```

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

With Docker, connect host tools to MQTT on `localhost:1884`. The Python gateway and subscriber still use `1883` when they run inside Docker.

If you run the Python scripts on your Mac while the MQTT broker is running in Docker, set `MQTT_PORT=1884`. In separate terminals, run:

```bash
python src/modbus_simulator.py
MQTT_PORT=1884 python src/modbus_to_mqtt_gateway.py
MQTT_PORT=1884 python src/mqtt_subscriber.py
MQTT_PORT=1884 DASHBOARD_HOST=127.0.0.1 python src/dashboard.py
```

Then open `http://localhost:8080`.

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
