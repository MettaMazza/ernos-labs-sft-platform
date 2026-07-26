from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.inflation_growth_empirical_v1 import SPEC
from sft.physics.inflation_growth_validation_v1 import authoritative_record, exact_inflation_analysis


ROOT = Path(__file__).resolve().parents[1]


class InflationGrowthEmpiricalTests(unittest.TestCase):
    def test_complete_source_record(self) -> None:
        record = authoritative_record(ROOT)
        self.assertEqual(len(record["sources"]), 2)
        self.assertFalse(record["historical_blindness_claimed"])

    def test_scalar_and_tensor_values_pass_exactly(self) -> None:
        analysis = exact_inflation_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertEqual(analysis["scalar_prediction"], Fraction(31, 32))
        self.assertEqual(analysis["scalar_interval"], (Fraction(9607, 10000), Fraction(9691, 10000)))
        self.assertTrue(analysis["scalar_inside_interval"])
        self.assertEqual(analysis["tensor_prediction"], Fraction(1, 32))
        self.assertEqual(analysis["tensor_upper_bound"], Fraction(4, 125))
        self.assertTrue(analysis["tensor_strictly_below_bound"])
        self.assertEqual(analysis["tensor_bound_margin"], Fraction(3, 4000))
        self.assertTrue(analysis["partition_complete"])

    def test_tampered_scalar_value_fails(self) -> None:
        target = dict(authoritative_record(ROOT)["registered_target"])
        target["planck_scalar_index_central"] = "0.9000"
        self.assertFalse(exact_inflation_analysis(target)["scalar_inside_interval"])

    def test_complete_empirical_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
