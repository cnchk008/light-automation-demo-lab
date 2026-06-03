import random
from dataclasses import dataclass

from pymodbus import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

from config import MODBUS_HOST, MODBUS_PORT, MODBUS_UNIT_ID
from registers import REGISTER_COUNT, registers_to_payload


@dataclass
class CellState:
    cycle_count: int = 0
    downtime_seconds: int = 0

    def next_registers(self) -> list[int]:
        part_present = random.choice([0, 1, 1])
        safety_gate_closed = random.choice([1, 1, 1, 1, 0])
        emergency_stop_ok = random.choice([1, 1, 1, 1, 1, 0])
        robot_busy = random.choice([0, 1, 1])

        if not safety_gate_closed:
            fault_code = 101
            self.downtime_seconds += 5
            robot_busy = 0
        elif not emergency_stop_ok:
            fault_code = 201
            self.downtime_seconds += 5
            robot_busy = 0
        else:
            fault_code = 0

        if part_present and safety_gate_closed and emergency_stop_ok and robot_busy:
            self.cycle_count += 1

        return [
            part_present,
            safety_gate_closed,
            emergency_stop_ok,
            robot_busy,
            fault_code,
            self.cycle_count,
            random.randint(8, 14),
            self.downtime_seconds,
        ]


state = CellState()


async def refresh_registers(
    function_code: int,
    start_address: int,
    address: int,
    count: int,
    current_registers: list[int],
    set_values: list[int] | list[bool] | None,
) -> None:
    if set_values is not None or function_code not in {3, 4}:
        return

    values = state.next_registers()
    current_registers[:REGISTER_COUNT] = values
    payload = registers_to_payload(values)
    print(f"Simulator registers @ {start_address}: {values} -> {payload['status']}")


def device_identity() -> ModbusDeviceIdentification:
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Demo Automation Lab"
    identity.ProductCode = "LADL"
    identity.ProductName = "Light Automation Cobot Cell Simulator"
    identity.ModelName = "Cobot Cell 01"
    identity.MajorMinorRevision = "1.0"
    return identity


def run_server() -> None:
    device = SimDevice(
        id=MODBUS_UNIT_ID,
        simdata=SimData(
            address=0,
            count=100,
            values=0,
            datatype=DataType.REGISTERS,
        ),
        identity=device_identity(),
        action=refresh_registers,
    )

    print(f"Starting Modbus TCP simulator on {MODBUS_HOST}:{MODBUS_PORT}")
    StartTcpServer(device, address=(MODBUS_HOST, MODBUS_PORT))


if __name__ == "__main__":
    run_server()
