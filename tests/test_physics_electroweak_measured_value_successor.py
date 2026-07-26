import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.electroweak_measured_value_successor_validation_v1 import authoritative_record, exact_electroweak_analysis
from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.electroweak_measured_value_successor_v1 import SOURCE_IDS, SPEC


class ElectroweakMeasuredValueSuccessorTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_measured_value_vector(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_electroweak_analysis(record["registered_target"])
        self.assertEqual(result["direct_on_shell_interval"], (Fraction(22333, 100000), Fraction(22351, 100000)))
        ignored = {"direct_on_shell_interval", "compatible_WZ_squared_interval", "all_input_WZ_squared_method_record"}
        self.assertTrue(all(value for key, value in result.items() if key not in ignored))

    def test_tampered_direct_measurement_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["on_shell_sin_squared_center"] = "0.22000"
        self.assertFalse(exact_electroweak_analysis(target)["forced_sine_inside_direct_interval"])

    def test_tampered_compatible_W_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["compatible_w_mass_GeV"] = "81"
        self.assertFalse(exact_electroweak_analysis(target)["forced_cosine_inside_compatible_WZ_interval"])


if __name__ == "__main__":
    unittest.main()
