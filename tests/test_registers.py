import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from registers import REGISTER_COUNT, registers_to_payload


class RegisterPayloadTest(unittest.TestCase):
    def test_converts_registers_to_payload(self) -> None:
        payload = registers_to_payload(
            [1, 1, 1, 0, 0, 12, 10, 5],
            timestamp="2026-06-03T09:00:00+00:00",
        )

        self.assertEqual(payload["cell_id"], "cobot_cell_01")
        self.assertEqual(payload["timestamp"], "2026-06-03T09:00:00+00:00")
        self.assertTrue(payload["status"]["part_present"])
        self.assertTrue(payload["status"]["safety_gate_closed"])
        self.assertTrue(payload["status"]["emergency_stop_ok"])
        self.assertFalse(payload["status"]["robot_busy"])
        self.assertEqual(payload["status"]["fault_label"], "none")
        self.assertEqual(payload["metrics"]["cycle_count"], 12)
        self.assertEqual(payload["metrics"]["average_cycle_time_seconds"], 10)
        self.assertEqual(payload["metrics"]["downtime_seconds"], 5)

    def test_labels_known_faults(self) -> None:
        payload = registers_to_payload([0, 0, 1, 0, 101, 7, 12, 20])

        self.assertEqual(payload["status"]["fault_label"], "safety_gate_open")

    def test_rejects_short_register_list(self) -> None:
        with self.assertRaisesRegex(ValueError, str(REGISTER_COUNT)):
            registers_to_payload([1, 1, 1])


if __name__ == "__main__":
    unittest.main()
