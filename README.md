# Light Automation Demo Lab

A small, runnable demo for a machine-tending light automation cell.

It simulates a Modbus TCP cobot, a Profinet part feeder, and a safety light curtain, reads the devices through gateways, converts their machine-facing data into JSON, and publishes the results to MQTT.

## What it shows

- A cobot cell simulator exposing eight Modbus holding registers.
- A Profinet-style cyclic I/O part feeder simulator.
- A Profinet Safety-style light curtain simulator.
- A Modbus-to-MQTT gateway that publishes production status.
- A Profinet-to-MQTT gateway that publishes feeder status.
- A safety-to-MQTT gateway that publishes beam and OSSD status.
- A local Mosquitto broker for testing.
- A subscriber helper that prints the MQTT messages.
- A browser dashboard for live device visualization.
- A simple ROI calculator for the automation business case.

## Architecture

```text
Modbus cobot simulator -------> Modbus-to-MQTT gateway ----\
                                                           +-> MQTT broker -> subscriber/dashboard
Profinet feeder simulator ---> Profinet-to-MQTT gateway ---/
Safety light curtain --------> Safety-to-MQTT gateway -----/
```

The main topics are:

```text
factory/light_automation/cobot_cell_01/status
factory/light_automation/profinet_feeder_01/status
factory/light_automation/safety_light_curtain_01/status
```

The dashboard and subscriber use the wildcard topic `factory/light_automation/+/status` when run with Docker, so both devices appear in the same stream.

## Run with Docker

```bash
docker compose up --build
```

You should see the Modbus simulator updating registers, the Profinet simulator sending feeder process images, the light curtain simulator sending safety process images, all gateways publishing JSON, and the subscriber printing messages from every device.

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
PROFINET_HOST=127.0.0.1 MQTT_PORT=1884 python src/profinet_to_mqtt_gateway.py
PROFINET_GATEWAY_HOST=127.0.0.1 python src/profinet_simulator.py
SAFETY_HOST=127.0.0.1 MQTT_PORT=1884 python src/safety_to_mqtt_gateway.py
SAFETY_GATEWAY_HOST=127.0.0.1 python src/safety_light_curtain_simulator.py
MQTT_PORT=1884 MQTT_TOPIC_FILTER='factory/light_automation/+/status' python src/mqtt_subscriber.py
MQTT_PORT=1884 MQTT_TOPIC_FILTER='factory/light_automation/+/status' DASHBOARD_HOST=127.0.0.1 python src/dashboard.py
```

Then open `http://localhost:8080`.

## Modbus Register Map

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

## Profinet Process Image

The Profinet feeder simulator sends a compact binary process image over UDP to keep the demo runnable in Docker without raw industrial Ethernet privileges. The gateway treats that process image as cyclic Profinet I/O and normalizes it to MQTT.

| Field | Type | Meaning |
| --- | --- | --- |
| `feeder_running` | byte | 1 when the feeder is moving parts |
| `transfer_ready` | byte | 1 when a part is ready for the cobot |
| `buffer_level_percent` | unsigned 16-bit | feeder buffer level |
| `fault_code` | unsigned 16-bit | 0, 301, 302, or 303 |
| `feed_count` | unsigned 16-bit | completed simulated feeds |
| `jam_count` | unsigned 16-bit | accumulated simulated jams |
| `uptime_seconds` | unsigned 16-bit | simulated feeder uptime |

## Safety Light Curtain Process Image

The light curtain simulator sends a separate compact safety process image over UDP. It represents the kind of state a safety PLC or safety I/O block would expose after a light curtain is wired into the cell.

| Field | Type | Meaning |
| --- | --- | --- |
| `beam_clear` | byte | 1 when the protected field is clear |
| `muted` | byte | 1 when muting is active |
| `reset_required` | byte | 1 when a manual reset is latched |
| `ossd_outputs_on` | byte | 1 when safety outputs are enabled |
| `fault_code` | unsigned 16-bit | 0, 401, 402, or 403 |
| `interruption_count` | unsigned 16-bit | accumulated beam interruptions |
| `last_interruption_ms` | unsigned 16-bit | simulated duration of the last stop |

## Example Payload

```json
{
  "cell_id": "cobot_cell_01",
  "protocol": "modbus_tcp",
  "device_type": "cobot_cell",
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

```json
{
  "cell_id": "profinet_feeder_01",
  "protocol": "profinet",
  "device_type": "part_feeder",
  "timestamp": "2026-06-03T09:00:00+00:00",
  "status": {
    "feeder_running": true,
    "transfer_ready": true,
    "buffer_level_percent": 74,
    "fault_code": 0,
    "fault_label": "none"
  },
  "metrics": {
    "feed_count": 18,
    "jam_count": 1,
    "uptime_seconds": 120
  }
}
```

```json
{
  "cell_id": "safety_light_curtain_01",
  "protocol": "profinet_safety",
  "device_type": "light_curtain",
  "timestamp": "2026-06-03T09:00:00+00:00",
  "status": {
    "beam_clear": false,
    "muted": false,
    "reset_required": true,
    "ossd_outputs_on": false,
    "fault_code": 401,
    "fault_label": "beam_interrupted"
  },
  "metrics": {
    "interruption_count": 4,
    "last_interruption_ms": 620
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
