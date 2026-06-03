import random
import threading
import time

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer

from config import MODBUS_HOST, MODBUS_PORT


# Holding register map:
# 0 = part_present
# 1 = safety_gate_closed
# 2 = emergency_stop_ok
# 3 = robot_busy
# 4 = fault_code
# 5 = cycle_count
# 6 = average_cycle_time_seconds
# 7 = downtime_seconds


def update_registers(context):
    cycle_count = 0
    downtime_seconds = 0

    while True:
        part_present = random.choice([0, 1])
        safety_gate_closed = random.choice([1, 1, 1, 0])
        emergency_stop_ok = random.choice([1, 1, 1, 1, 0])
        robot_busy = random.choice([0, 1])

        if safety_gate_closed == 0:
            fault_code = 101
            downtime_seconds += 5
        elif emergency_stop_ok == 0:
            fault_code = 201
            downtime_seconds += 5
        else:
            fault_code = 0

        if part_present == 1 and safety_gate_closed == 1 and emergency_stop_ok == 1:
            cycle_count += 1

        average_cycle_time = random.randint(8, 14)

        values = [
            part_present,
            safety_gate_closed,
            emergency_stop_ok,
            robot_busy,
            fault_code,
            cycle_count,
            average_cycle_time,
            downtime_seconds,
        ]

        context[0].setValues(3, 0, values)
        print(f"Updated Modbus registers: {values}")

        time.sleep(5)


def run_server():
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 100)
    )

    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = "Demo Automation Lab"
    identity.ProductCode = "LADL"
    identity.ProductName = "Light Automation Cobot Cell Simulator"
    identity.ModelName = "Cobot Cell 01"
    identity.MajorMinorRevision = "1.0"

    updater = threading.Thread(target=update_registers, args=(context,), daemon=True)
    updater.start()

    print(f"Starting Modbus TCP simulator on {MODBUS_HOST}:{MODBUS_PORT}")

    StartTcpServer(
        context=context,
        identity=identity,
        address=(MODBUS_HOST, MODBUS_PORT),
    )


if __name__ == "__main__":
    run_server()