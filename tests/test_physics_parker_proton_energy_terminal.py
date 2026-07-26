from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.parker_proton_energy_terminal_law_v1 import (
    SPEC,
    historical_leading_fraction,
    proton_energy_fraction,
    structural_formula_census,
)
from sft.physics.parker_proton_energy_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
)
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class ParkerProtonEnergyTerminalTests(unittest.TestCase):
    def test_exact_fractions(self) -> None:
        self.assertEqual(historical_leading_fraction(), Fraction(500000, 1173679081))
        self.assertEqual(proton_energy_fraction(), Fraction(108147617771025486368, 253861190227103943729961))

    def test_complete_formula_census(self) -> None:
        rows = structural_formula_census()
        self.assertEqual(len(rows), 12)
        self.assertEqual(sum(row["structurally_selected"] for row in rows), 1)

    def test_complete_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 3072)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 3072)

    def test_precision_nonclaim(self) -> None:
        SPEC.validate()
        self.assertTrue(
            any(
                "no claim that approximately 400 keV is an exact" in exclusion
                for exclusion in SPEC.exclusions
            )
        )

    def test_complete_postseal_comparison(self) -> None:
        target = authoritative_record(ROOT)["registered_target"]
        analysis = exact_measurement_analysis(target)
        self.assertTrue(analysis["terminal_inside_complete_range"])
        self.assertTrue(analysis["leading_inside_complete_range"])
        self.assertFalse(analysis["approximate_label_has_uncertainty"])
        self.assertFalse(analysis["approximate_label_is_exact_cutoff"])
        self.assertFalse(analysis["observation_uniquely_selects_structural_formula"])
        self.assertIn((2, 2), analysis["adverse_inside_range"])
        self.assertIn((3, 2), analysis["adverse_inside_range"])


if __name__ == "__main__":
    unittest.main()
