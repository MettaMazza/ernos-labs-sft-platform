from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.proton_radius_terminal_law_v1 import (
    SPEC,
    colour_fibre_support,
    complete_charge_support,
    leading_radius_multiplier,
    proton_edge_share,
    proton_inner_site,
    structural_formula_census,
    terminal_radius_coefficient,
)
from sft.physics.proton_radius_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
)
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class ProtonRadiusTerminalTests(unittest.TestCase):
    def test_exact_structure(self) -> None:
        self.assertEqual(proton_inner_site(), Fraction(1, 3))
        self.assertEqual(proton_edge_share(), Fraction(2, 3))
        self.assertEqual(colour_fibre_support(), 6)
        self.assertEqual(leading_radius_multiplier(), 4)
        self.assertEqual(complete_charge_support(), 10)
        self.assertEqual(terminal_radius_coefficient(), Fraction(10069574419808, 2519231977345))

    def test_complete_formula_controls(self) -> None:
        rows = structural_formula_census()
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(row["structurally_selected"] for row in rows), 1)

    def test_complete_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2304)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2304)

    def test_scope(self) -> None:
        SPEC.validate()
        self.assertTrue(any("hard material edge" in item for item in SPEC.exclusions))
        self.assertTrue(any("historical" in item for item in SPEC.exclusions))

    def test_complete_current_and_adverse_comparison(self) -> None:
        target = authoritative_record(ROOT)["registered_target"]
        analysis = exact_measurement_analysis(target)
        self.assertTrue(analysis["all_current_intervals_contain_prediction"])
        self.assertTrue(analysis["historical_conflict_retained"])
        self.assertFalse(analysis["observation_uniquely_selects_ten_linear"])
        self.assertEqual(
            analysis["adverse_inside_muonic_interval"],
            ((8, "linear"), (9, "linear"), (10, "linear")),
        )


if __name__ == "__main__":
    unittest.main()
