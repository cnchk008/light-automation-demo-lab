import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from inspection_io import InspectionProcessImage, process_image_to_payload


class InspectionProcessImageTest(unittest.TestCase):
    def test_round_trips_binary_process_image(self) -> None:
        image = InspectionProcessImage(
            camera_online=True,
            part_detected=True,
            inspection_passed=True,
            confidence_percent=94,
            fault_code=0,
            inspection_count=12,
            reject_count=2,
            average_inspection_ms=185,
        )

        decoded = InspectionProcessImage.from_bytes(image.to_bytes())

        self.assertEqual(decoded, image)

    def test_converts_process_image_to_payload(self) -> None:
        image = InspectionProcessImage(
            camera_online=True,
            part_detected=True,
            inspection_passed=False,
            confidence_percent=78,
            fault_code=502,
            inspection_count=13,
            reject_count=3,
            average_inspection_ms=210,
        )

        payload = process_image_to_payload(
            image,
            device_id="vision_camera_01",
            timestamp="2026-06-03T09:00:00+00:00",
        )

        self.assertEqual(payload["cell_id"], "vision_camera_01")
        self.assertEqual(payload["protocol"], "ethernet_ip")
        self.assertEqual(payload["device_type"], "vision_inspection")
        self.assertEqual(payload["status"]["fault_label"], "low_confidence")
        self.assertFalse(payload["status"]["inspection_passed"])
        self.assertEqual(payload["metrics"]["inspection_count"], 13)
        self.assertEqual(payload["metrics"]["reject_count"], 3)

    def test_rejects_short_process_image(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected at least"):
            InspectionProcessImage.from_bytes(b"\x01")


if __name__ == "__main__":
    unittest.main()
