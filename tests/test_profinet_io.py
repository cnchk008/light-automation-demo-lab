import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from profinet_io import ProfinetProcessImage, process_image_to_payload


class ProfinetProcessImageTest(unittest.TestCase):
    def test_round_trips_binary_process_image(self) -> None:
        image = ProfinetProcessImage(
            feeder_running=True,
            transfer_ready=True,
            buffer_level_percent=74,
            fault_code=0,
            feed_count=18,
            jam_count=1,
            uptime_seconds=120,
        )

        decoded = ProfinetProcessImage.from_bytes(image.to_bytes())

        self.assertEqual(decoded, image)

    def test_converts_process_image_to_payload(self) -> None:
        image = ProfinetProcessImage(
            feeder_running=False,
            transfer_ready=False,
            buffer_level_percent=9,
            fault_code=302,
            feed_count=20,
            jam_count=2,
            uptime_seconds=180,
        )

        payload = process_image_to_payload(
            image,
            device_id="profinet_feeder_01",
            timestamp="2026-06-03T09:00:00+00:00",
        )

        self.assertEqual(payload["cell_id"], "profinet_feeder_01")
        self.assertEqual(payload["protocol"], "profinet")
        self.assertEqual(payload["device_type"], "part_feeder")
        self.assertEqual(payload["status"]["fault_label"], "low_buffer")
        self.assertEqual(payload["status"]["buffer_level_percent"], 9)
        self.assertEqual(payload["metrics"]["feed_count"], 20)
        self.assertEqual(payload["metrics"]["jam_count"], 2)

    def test_rejects_short_process_image(self) -> None:
        with self.assertRaisesRegex(ValueError, "Expected at least"):
            ProfinetProcessImage.from_bytes(b"\x01")


if __name__ == "__main__":
    unittest.main()
