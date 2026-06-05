# Architecture

This lab demonstrates a lightweight industrial integration pattern:

```text
Modbus cobot registers --------> Modbus-to-MQTT gateway ----\
                                                            +-> Broker, dashboard, historian, or automation monitor
Profinet feeder process image -> Profinet-to-MQTT gateway --/
```

The first simulator represents a small cobot machine-tending cell. It exposes a compact holding-register map with safety, production, and downtime signals. The second simulator represents a Profinet part feeder that sends cyclic process images. Each gateway reads the machine-facing protocol and publishes a normalized JSON message to MQTT.

This is intentionally small enough to run on a laptop but close enough to a real automation stack to discuss integration tradeoffs, data ownership, downtime visibility, and ROI.
