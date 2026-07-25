from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.scattering_rutherford_compton_terminal_law_v1 import (
    ScatteringRutherfordComptonProgram,
    TRANSFER_PARTS,
    annular_transfer_density,
    candidate_forms,
    compton_conservation_transfer,
    cumulative_impact_area,
    formal_certificate,
    form_survives,
    forward_transfer,
    high_energy_ceiling_in_rest_units,
    high_energy_gap,
    high_energy_step,
    paired_overlap_density,
    photon_shift_in_compton_carriers,
    scattered_photon_energy_ratio,
)
from sft.physics.scattering_rutherford_compton_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class ScatteringRutherfordComptonTerminalTests(unittest.TestCase):
    def test_complete_product_has_one_computed_form(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2916)
        self.assertEqual(len({form.candidate_id for form in forms}), 2916)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0].coulomb_angular_law, "inverse-transfer-part-squared")
        self.assertEqual(
            survivors[0].photon_shift_law,
            "two-transfer-parts-times-action-over-inertia-speed",
        )

    def test_exact_rutherford_geometry_forces_inverse_fourth_half_angle_translation(self):
        self.assertEqual(forward_transfer(), ())
        self.assertEqual(
            tuple(paired_overlap_density(part) for part in TRANSFER_PARTS),
            (Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1)),
        )
        self.assertEqual(cumulative_impact_area(Fraction(1, 1)), ())
        for lower, upper in zip(TRANSFER_PARTS, TRANSFER_PARTS[1:]):
            self.assertEqual(
                annular_transfer_density(lower, upper),
                Fraction(1, 1) / (lower * upper),
            )

    def test_exact_compton_transfer_and_high_energy_ceiling(self):
        shifts = tuple(photon_shift_in_compton_carriers(part) for part in TRANSFER_PARTS)
        self.assertEqual(
            shifts,
            (Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1)),
        )
        for part, shift in zip(TRANSFER_PARTS, shifts):
            ratio = scattered_photon_energy_ratio(Fraction(1, 1), part)
            self.assertEqual(compton_conservation_transfer(Fraction(1, 1), ratio), shift)
            for depth in (1, 2, 3, 4):
                self.assertGreater(high_energy_step(depth, part), 0)
                self.assertGreater(high_energy_gap(depth, part), 0)
        self.assertEqual(high_energy_ceiling_in_rest_units(Fraction(1, 2)), Fraction(1, 1))
        self.assertEqual(high_energy_ceiling_in_rest_units(Fraction(1, 1)), Fraction(1, 2))

    def test_complete_external_comparison_closes_iaea_and_nist_values(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(ROOT)
        self.assertEqual(len(record["sources"]), 2)
        self.assertEqual(analysis["codata"]["row_count"], 7)
        self.assertTrue(analysis["codata"]["derived_reported_intervals_overlap"])
        self.assertTrue(analysis["codata"]["iaea_rounded_compton_carrier_contains_nist"])
        self.assertTrue(analysis["iaea"]["rutherford_relation_complete"])
        self.assertTrue(analysis["iaea"]["large_angle_observed_support"])
        self.assertTrue(analysis["iaea"]["compton_relation_complete"])
        self.assertTrue(analysis["rutherford_exact_vector_matches"])
        self.assertTrue(analysis["compton_exact_vector_matches"])

    def test_controls_and_formal_source_exclude_targets_answers_and_numeric_null(self):
        program = ScatteringRutherfordComptonProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))
        certificate = formal_certificate()
        self.assertEqual(certificate["forward_transfer"], ())
        source = (
            ROOT / "sft/physics/scattering_rutherford_compton_terminal_law_v1.py"
        ).read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("expected_survivor", lowered)
        self.assertNotIn('"admitted": true', lowered)
        self.assertNotIn("fraction(0", lowered)


if __name__ == "__main__":
    unittest.main()
