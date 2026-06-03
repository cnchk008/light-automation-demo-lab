import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from roi_calculator import calculate_payback_years


class RoiCalculatorTest(unittest.TestCase):
    def test_calculates_payback(self) -> None:
        self.assertEqual(calculate_payback_years(120_000, 60_000), 2)

    def test_returns_none_without_savings(self) -> None:
        self.assertIsNone(calculate_payback_years(120_000, 0))


if __name__ == "__main__":
    unittest.main()
