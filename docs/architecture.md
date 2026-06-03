# Architecture

This lab demonstrates a lightweight industrial integration pattern:

```text
Simulated machine registers
        |
        | Modbus TCP
        v
Modbus-to-MQTT gateway
        |
        | JSON over MQTT
        v
Broker, dashboard, historian, or automation monitor
```

The simulator represents a small cobot machine-tending cell. It exposes a compact holding-register map with safety, production, and downtime signals. The gateway polls that map and publishes a normalized JSON message to MQTT.

This is intentionally small enough to run on a laptop but close enough to a real automation stack to discuss integration tradeoffs, data ownership, downtime visibility, and ROI.
