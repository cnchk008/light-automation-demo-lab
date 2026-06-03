# Protocol Comparison

## Modbus TCP

Modbus is common in industrial devices and PLC-adjacent equipment. It is simple, deterministic, and easy to inspect, but raw registers need a map before they are meaningful to software teams.

## MQTT

MQTT is lightweight publish/subscribe messaging. It works well for sending normalized machine events and status snapshots to dashboards, cloud services, or local monitoring systems.

## Why bridge them?

The bridge keeps the machine-facing protocol close to the automation cell while exposing a friendlier data stream for applications. In this repo, eight Modbus registers become one JSON MQTT status payload.
