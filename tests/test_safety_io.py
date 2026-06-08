import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from safety_io import SafetyProcessImage, process_image_to_payload


class SafetyProcessImageTest(unittest.TestCase):
    def test_round_trips_binary_process_image(self) -> None:
        image = SafetyProcessImage(
            beam_clear=True,
            muted=False,
            reset_required=False,
            ossd_outputs_on=True,
            fault_code=0,
            interruption_count=3,
            last_interruption_ms=250,
        )

        decoded = SafetyProcessImage.from_bytes(image.to_bytes())

        self.assertEqual(decoded, image)

    def test_converts_process_image_to_payload(self) -> None:
        image = SafetyProcessImage(
            beam_clear=False,
            muted=False,
            reset_required=True,
            ossd_outputs_on=False,
            fault_code=401,
            interruption_count=4,
            last_interruption_ms=620,
        )

        payload = process_image_to_payload(
            image,
            device_id="safety_light_curtain_01",
            timestamp="2026-06-03T09:00:00+00:00",
        )

        self.assertEqual(payload["cell_id"], "safety_light_curtain_01")
        self.assertEqual(payload["protocol"], "profinet_safety")
        self.assertEqual(payload["device_type"], "light_curtain")
        self.assertEqual(payload["status"]["fault_label"], "beam_interrupted")
        self.assertFalse(payload["status"]["ossd_outputs_on"])
        self.assertEqual(payload["metrics"]["interruption_count"], 4)
        self.assertEqual(payload["metrics"]["last_interruption_ms"], 620)

    def test_rejects_short_process_image(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected at least"):
            SafetyProcessImage.from_bytes(b"\x01")


if __name__ == "__main__":
    unittest.main()
