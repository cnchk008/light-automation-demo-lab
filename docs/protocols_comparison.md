# Protocol Comparison

## Modbus TCP

Modbus is common in industrial devices and PLC-adjacent equipment. It is simple, deterministic, and easy to inspect, but raw registers need a map before they are meaningful to software teams.

## MQTT

MQTT is lightweight publish/subscribe messaging. It works well for sending normalized machine events and status snapshots to dashboards, cloud services, or local monitoring systems.

## Profinet

Profinet is common for real-time industrial I/O, especially around PLCs, drives, remote I/O, and feeder equipment. It is a better fit than Modbus when a controller expects cyclic process data and tighter machine coordination, but it usually needs more deliberate network setup.

## Why bridge them?

The bridge keeps the machine-facing protocol close to the automation cell while exposing a friendlier data stream for applications. In this repo, eight Modbus registers and one Profinet feeder process image become JSON MQTT status payloads.
