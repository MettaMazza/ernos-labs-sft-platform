from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from sft.live_measurement import LiveMeasurementError, run_live_measurement_checks
from sft.physics.charged_lepton_validation import SOURCE_PATH


class _Response:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self.payload


class LiveMeasurementTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.table = (root / SOURCE_PATH).read_bytes()

    def test_complete_current_table_passes_all_exact_checks(self) -> None:
        with patch("sft.live_measurement.urlopen", return_value=_Response(self.table)):
            report = run_live_measurement_checks()
        self.assertEqual(len(report.exact_checks), 5)

    def test_missing_authoritative_rows_halts(self) -> None:
        with patch("sft.live_measurement.urlopen", return_value=_Response(b"not CODATA")):
            with self.assertRaises(LiveMeasurementError):
                run_live_measurement_checks()

    def test_tampered_measured_value_halts(self) -> None:
        changed = self.table.replace(
            b"137.035 999 177",
            b"127.035 999 177",
            1,
        )
        self.assertNotEqual(changed, self.table)
        with patch("sft.live_measurement.urlopen", return_value=_Response(changed)):
            with self.assertRaises(LiveMeasurementError):
                run_live_measurement_checks()


if __name__ == "__main__":
    unittest.main()
