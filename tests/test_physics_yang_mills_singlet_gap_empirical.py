from __future__ import annotations

from pathlib import Path
import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.yang_mills_singlet_gap_empirical_v1 import SPEC
from sft.physics.yang_mills_singlet_gap_empirical_validation_v1 import (
    authoritative_record,
    exact_spectrum_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class YangMillsSingletGapEmpiricalTests(unittest.TestCase):
    def test_spec_and_candidate_product(self) -> None:
        SPEC.validate()
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_source_and_exact_intervals(self) -> None:
        target = authoritative_record(ROOT)["registered_target"]
        analysis = exact_spectrum_analysis(target)
        self.assertEqual(analysis["row_count"], 3)
        self.assertEqual(analysis["quantum_number_order"], ("0++", "2++", "0-+"))
        self.assertTrue(analysis["all_lower_edges_positive"])
        self.assertTrue(analysis["intervals_strictly_ordered_and_disjoint"])
        self.assertTrue(analysis["scope_rows_retained"])

    def test_nonclaim_is_explicit(self) -> None:
        self.assertIn("does not predict a dimensionful", SPEC.statement)
        self.assertIn("lack of an unambiguous experimental glueball", SPEC.exact_result)


if __name__ == "__main__":
    unittest.main()
