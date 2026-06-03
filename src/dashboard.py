from __future__ import annotations

import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import paho.mqtt.client as mqtt

from config import DASHBOARD_HOST, DASHBOARD_PORT, MQTT_HOST, MQTT_PORT, MQTT_TOPIC


clients: list[queue.Queue[dict]] = []
clients_lock = threading.Lock()
latest_payload: dict | None = None
latest_received_at: float | None = None
mqtt_connected = False


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Light Automation Dashboard</title>
  <style>
    :root {
      --ink: #1f2933;
      --muted: #687784;
      --line: #d8dee4;
      --panel: #ffffff;
      --page: #f4f7f5;
      --accent: #147d64;
      --warn: #b7791f;
      --fault: #c2413b;
      --ok-bg: #dff4eb;
      --warn-bg: #fff0c2;
      --fault-bg: #ffe2df;
      --shadow: 0 10px 24px rgba(31, 41, 51, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      color: var(--ink);
      background: var(--page);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }

    .shell {
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }

    header {
      background: #20343a;
      color: #f7fbf9;
      border-bottom: 4px solid #d7b46a;
    }

    .header-inner,
    main {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }

    .header-inner {
      min-height: 92px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }

    h1 {
      margin: 0;
      font-size: 28px;
      font-weight: 760;
    }

    .subhead {
      margin-top: 6px;
      color: #b9c8c5;
      font-size: 14px;
    }

    .connection {
      min-width: 166px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 8px 12px;
      border: 1px solid rgba(255, 255, 255, 0.28);
      border-radius: 8px;
      color: #eef8f5;
      background: rgba(255, 255, 255, 0.08);
      font-size: 13px;
      white-space: nowrap;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #cbd5dc;
    }

    .dot.ok {
      background: #51c878;
    }

    .dot.warn {
      background: #ecc94b;
    }

    main {
      padding: 28px 0 36px;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
      align-items: start;
    }

    .panel,
    .metric,
    .signal {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .panel {
      padding: 18px;
    }

    .section-title {
      margin: 0 0 14px;
      font-size: 16px;
      font-weight: 720;
    }

    .cell-status {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 18px;
      align-items: center;
    }

    .machine {
      width: 190px;
      aspect-ratio: 1;
      border-radius: 8px;
      background: #e6ece9;
      border: 1px solid var(--line);
      position: relative;
      overflow: hidden;
    }

    .machine::before {
      content: "";
      position: absolute;
      inset: 24px 22px 54px;
      border: 12px solid #6a7d83;
      border-bottom-width: 18px;
      border-radius: 8px;
      background: #d2dad7;
    }

    .arm {
      position: absolute;
      left: 62px;
      top: 48px;
      width: 94px;
      height: 18px;
      border-radius: 8px;
      background: #d7b46a;
      transform-origin: 18px 9px;
      transform: rotate(-16deg);
      transition: transform 400ms ease;
    }

    .busy .arm {
      animation: work 1.4s ease-in-out infinite alternate;
    }

    .gripper {
      position: absolute;
      right: 29px;
      top: 86px;
      width: 28px;
      height: 44px;
      border: 7px solid #20343a;
      border-top: 0;
      border-radius: 0 0 8px 8px;
    }

    .part {
      position: absolute;
      left: 70px;
      bottom: 28px;
      width: 50px;
      height: 30px;
      border-radius: 6px;
      background: #147d64;
      opacity: 0.18;
      transition: opacity 220ms ease;
    }

    .part.present {
      opacity: 1;
    }

    .fault .machine,
    .fault.machine {
      background: var(--fault-bg);
      border-color: #efb0aa;
    }

    @keyframes work {
      from { transform: rotate(-22deg); }
      to { transform: rotate(22deg); }
    }

    .state-stack {
      display: grid;
      gap: 10px;
    }

    .fault-banner {
      min-height: 54px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--ok-bg);
      border: 1px solid #b9e4d3;
    }

    .fault-banner.warning {
      background: var(--fault-bg);
      border-color: #efb0aa;
    }

    .fault-code {
      color: var(--muted);
      font-size: 13px;
    }

    .signals {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    .signal {
      min-height: 72px;
      padding: 12px;
      display: grid;
      align-content: center;
      gap: 6px;
      box-shadow: none;
    }

    .label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }

    .value {
      font-size: 18px;
      font-weight: 760;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .metric {
      min-height: 112px;
      padding: 14px;
      display: grid;
      align-content: space-between;
    }

    .metric-value {
      font-size: 34px;
      font-weight: 780;
      color: #20343a;
    }

    .unit {
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }

    .chart-wrap {
      height: 260px;
    }

    canvas {
      width: 100%;
      height: 100%;
      display: block;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfdfc;
    }

    .footer-line {
      margin-top: 14px;
      color: var(--muted);
      font-size: 13px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    @media (max-width: 820px) {
      .header-inner {
        align-items: flex-start;
        flex-direction: column;
        justify-content: center;
        padding: 18px 0;
      }

      .grid,
      .cell-status,
      .metrics {
        grid-template-columns: 1fr;
      }

      .machine {
        width: 100%;
        max-width: 260px;
      }

      .signals {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="header-inner">
        <div>
          <h1>Light Automation Dashboard</h1>
          <div class="subhead" id="cell-id">cobot_cell_01</div>
        </div>
        <div class="connection"><span class="dot warn" id="connection-dot"></span><span id="connection-text">Waiting for data</span></div>
      </div>
    </header>

    <main>
      <div class="grid">
        <section class="panel">
          <h2 class="section-title">Cell State</h2>
          <div class="cell-status" id="cell-state">
            <div class="machine" id="machine">
              <div class="arm"></div>
              <div class="gripper"></div>
              <div class="part" id="part"></div>
            </div>
            <div class="state-stack">
              <div class="fault-banner" id="fault-banner">
                <strong id="fault-label">No data</strong>
                <span class="fault-code" id="fault-code">Fault --</span>
              </div>
              <div class="signals">
                <div class="signal">
                  <div class="label">Safety Gate</div>
                  <div class="value" id="safety-gate">--</div>
                </div>
                <div class="signal">
                  <div class="label">E-Stop</div>
                  <div class="value" id="estop">--</div>
                </div>
                <div class="signal">
                  <div class="label">Robot</div>
                  <div class="value" id="robot">--</div>
                </div>
                <div class="signal">
                  <div class="label">Part</div>
                  <div class="value" id="part-present">--</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="panel">
          <h2 class="section-title">Production Metrics</h2>
          <div class="metrics">
            <div class="metric">
              <div class="label">Cycles</div>
              <div><span class="metric-value" id="cycles">--</span></div>
            </div>
            <div class="metric">
              <div class="label">Cycle Time</div>
              <div><span class="metric-value" id="cycle-time">--</span> <span class="unit">s</span></div>
            </div>
            <div class="metric">
              <div class="label">Downtime</div>
              <div><span class="metric-value" id="downtime">--</span> <span class="unit">s</span></div>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="trend" width="800" height="320"></canvas>
          </div>
          <div class="footer-line">
            <span id="updated-at">Last update --</span>
            <span>Topic factory/light_automation/cobot_cell_01/status</span>
          </div>
        </section>
      </div>
    </main>
  </div>

  <script>
    const history = [];
    const maxPoints = 36;
    const ids = {
      dot: document.getElementById("connection-dot"),
      connection: document.getElementById("connection-text"),
      cellId: document.getElementById("cell-id"),
      machine: document.getElementById("machine"),
      part: document.getElementById("part"),
      faultBanner: document.getElementById("fault-banner"),
      faultLabel: document.getElementById("fault-label"),
      faultCode: document.getElementById("fault-code"),
      safetyGate: document.getElementById("safety-gate"),
      estop: document.getElementById("estop"),
      robot: document.getElementById("robot"),
      partPresent: document.getElementById("part-present"),
      cycles: document.getElementById("cycles"),
      cycleTime: document.getElementById("cycle-time"),
      downtime: document.getElementById("downtime"),
      updatedAt: document.getElementById("updated-at"),
      trend: document.getElementById("trend")
    };

    function yesNo(value, yes, no) {
      return value ? yes : no;
    }

    function render(payload) {
      if (!payload || !payload.status || !payload.metrics) return;

      const status = payload.status;
      const metrics = payload.metrics;
      const faulted = Number(status.fault_code) !== 0;

      ids.dot.className = "dot ok";
      ids.connection.textContent = "Live";
      ids.cellId.textContent = payload.cell_id || "cobot_cell_01";
      ids.machine.classList.toggle("busy", Boolean(status.robot_busy));
      ids.machine.classList.toggle("fault", faulted);
      ids.part.classList.toggle("present", Boolean(status.part_present));
      ids.faultBanner.classList.toggle("warning", faulted);
      ids.faultLabel.textContent = faulted ? status.fault_label.replaceAll("_", " ") : "Normal";
      ids.faultCode.textContent = `Fault ${status.fault_code}`;
      ids.safetyGate.textContent = yesNo(status.safety_gate_closed, "Closed", "Open");
      ids.estop.textContent = yesNo(status.emergency_stop_ok, "Healthy", "Not OK");
      ids.robot.textContent = yesNo(status.robot_busy, "Busy", "Idle");
      ids.partPresent.textContent = yesNo(status.part_present, "Present", "Waiting");
      ids.cycles.textContent = metrics.cycle_count;
      ids.cycleTime.textContent = metrics.average_cycle_time_seconds;
      ids.downtime.textContent = metrics.downtime_seconds;
      ids.updatedAt.textContent = `Last update ${new Date(payload.timestamp).toLocaleTimeString()}`;

      history.push({
        cycle: Number(metrics.cycle_count || 0),
        downtime: Number(metrics.downtime_seconds || 0),
        cycleTime: Number(metrics.average_cycle_time_seconds || 0)
      });
      if (history.length > maxPoints) history.shift();
      drawTrend();
    }

    function drawTrend() {
      const canvas = ids.trend;
      const ctx = canvas.getContext("2d");
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "#fbfdfc";
      ctx.fillRect(0, 0, width, height);

      const pad = 34;
      ctx.strokeStyle = "#d8dee4";
      ctx.lineWidth = 1;
      for (let i = 0; i < 4; i += 1) {
        const y = pad + i * ((height - pad * 2) / 3);
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(width - pad, y);
        ctx.stroke();
      }

      drawLine(history.map((p) => p.cycle), "#147d64");
      drawLine(history.map((p) => p.cycleTime), "#d7a938");
      drawLine(history.map((p) => p.downtime), "#c2413b");

      ctx.font = "13px system-ui, sans-serif";
      ctx.fillStyle = "#147d64";
      ctx.fillText("cycles", pad, 20);
      ctx.fillStyle = "#b7791f";
      ctx.fillText("cycle time", pad + 76, 20);
      ctx.fillStyle = "#c2413b";
      ctx.fillText("downtime", pad + 176, 20);
    }

    function drawLine(values, color) {
      if (values.length < 2) return;
      const canvas = ids.trend;
      const ctx = canvas.getContext("2d");
      const pad = 34;
      const max = Math.max(1, ...values);
      const step = (canvas.width - pad * 2) / Math.max(1, values.length - 1);

      ctx.beginPath();
      values.forEach((value, index) => {
        const x = pad + index * step;
        const y = canvas.height - pad - (value / max) * (canvas.height - pad * 2);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.stroke();
    }

    const events = new EventSource("/events");
    events.addEventListener("snapshot", (event) => render(JSON.parse(event.data)));
    events.onerror = () => {
      ids.dot.className = "dot warn";
      ids.connection.textContent = "Reconnecting";
    };
  </script>
</body>
</html>
"""


def make_client() -> mqtt.Client:
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    return mqtt.Client()


def broadcast(payload: dict) -> None:
    with clients_lock:
        for client_queue in clients[:]:
            try:
                client_queue.put_nowait(payload)
            except queue.Full:
                clients.remove(client_queue)


def on_connect(client, userdata, flags, reason_code, properties=None) -> None:
    global mqtt_connected
    mqtt_connected = True
    print(f"Dashboard connected to MQTT with result {reason_code}")
    client.subscribe(MQTT_TOPIC)


def on_disconnect(client, userdata, flags=None, reason_code=None, properties=None) -> None:
    global mqtt_connected
    mqtt_connected = False
    print(f"Dashboard disconnected from MQTT: {reason_code}")


def on_message(client, userdata, message) -> None:
    global latest_payload, latest_received_at
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        return

    latest_payload = payload
    latest_received_at = time.time()
    broadcast(payload)


def mqtt_worker() -> None:
    while True:
        client = make_client()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except OSError as exc:
            print(f"Dashboard waiting for MQTT: {exc}")
            time.sleep(2)


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
            return

        if self.path == "/events":
            self.stream_events()
            return

        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            health = {
                "mqtt_connected": mqtt_connected,
                "has_payload": latest_payload is not None,
            }
            self.wfile.write(json.dumps(health).encode("utf-8"))
            return

        self.send_error(404)

    def stream_events(self) -> None:
        client_queue: queue.Queue[dict] = queue.Queue(maxsize=10)
        with clients_lock:
            clients.append(client_queue)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        try:
            if latest_payload is not None:
                self.send_snapshot(latest_payload)

            while True:
                try:
                    payload = client_queue.get(timeout=15)
                    self.send_snapshot(payload)
                except queue.Empty:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            with clients_lock:
                if client_queue in clients:
                    clients.remove(client_queue)

    def send_snapshot(self, payload: dict) -> None:
        data = json.dumps(payload)
        self.wfile.write(f"event: snapshot\ndata: {data}\n\n".encode("utf-8"))
        self.wfile.flush()

    def log_message(self, format: str, *args) -> None:
        return


def run_dashboard() -> None:
    threading.Thread(target=mqtt_worker, daemon=True).start()
    server = ThreadingHTTPServer((DASHBOARD_HOST, DASHBOARD_PORT), DashboardHandler)
    print(f"Dashboard listening on http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Dashboard stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_dashboard()
