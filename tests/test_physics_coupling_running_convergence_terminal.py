from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.coupling_running_convergence_terminal_law_v1 import (
    CouplingRunningConvergenceProgram,
    candidate_forms,
    carrier_translation_record,
    common_scale_vector,
    convergence_witness,
    coupling_shortfall,
    coupling_successor_take,
    formal_certificate,
    form_survives,
    generated_scale_support,
    generator_indexed_coupling,
    generator_pair_gap,
    pair_gap_successor_take,
)
from sft.physics.coupling_running_convergence_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class CouplingRunningConvergenceTerminalTests(unittest.TestCase):
    def test_complete_product_has_one_computed_form(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 8748)
        self.assertEqual(len({form.candidate_id for form in forms}), 8748)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(
            survivors[0].coupling_form,
            "holding-share-of-sector-plus-support",
        )
        self.assertEqual(
            survivors[0].convergence_law,
            "finite-positive-epsilon-witness-for-every-pair",
        )

    def test_exact_common_scale_running_and_gap_laws(self):
        self.assertEqual(
            tuple(generated_scale_support(level) for level in (1, 2, 3, 4, 5, 6)),
            (1, 2, 4, 8, 16, 32),
        )
        self.assertEqual(generator_indexed_coupling(2, 3), Fraction(5, 6))
        self.assertEqual(coupling_shortfall(2, 3), Fraction(1, 6))
        self.assertEqual(generator_pair_gap(2, 3, 3), Fraction(1, 42))
        self.assertEqual(
            dict(common_scale_vector(1)),
            {2: Fraction(2, 3), 3: Fraction(3, 4), 5: Fraction(5, 6), 7: Fraction(7, 8)},
        )

    def test_successors_raise_shares_shrink_gaps_and_close_every_tolerance(self):
        for sector in (2, 3, 5, 7):
            for level in (1, 2, 3, 4, 5):
                self.assertGreater(coupling_successor_take(sector, level), 0)
        for lower in (2, 3, 5):
            for upper in (3, 5, 7):
                if lower < upper:
                    for level in (1, 2, 3, 4, 5):
                        self.assertGreater(pair_gap_successor_take(lower, upper, level), 0)
                    for denominator in (1, 2, 3, 5, 7, 11, 17):
                        witness = convergence_witness(lower, upper, denominator)
                        self.assertTrue(witness["gap_below_tolerance"])
                        self.assertTrue(witness["binary_support_reaches_required_bound"])

    def test_complete_pdg_comparison_closes_declared_measurement_boundary(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(ROOT)
        self.assertEqual(len(record["sources"]), 3)
        self.assertEqual(analysis["strong"]["table_9_1_row_count"], 7)
        self.assertEqual(analysis["strong"]["figure_9_4_class_count"], 9)
        self.assertEqual(analysis["electromagnetic"]["alpha_zero_row_count"], 5)
        self.assertEqual(analysis["electromagnetic"]["delta_alpha_row_count"], 11)
        self.assertTrue(analysis["strong"]["separated_intervals_strictly_decrease_with_energy"])
        self.assertTrue(analysis["electromagnetic"]["therefore_alpha_strictly_increases_to_z_scale"])
        self.assertTrue(analysis["carrier_specific_opposite_energy_directions_retained"])
        self.assertTrue(analysis["formal_convergence_not_promoted_to_direct_measurement"])

    def test_controls_and_formal_source_exclude_targets_answers_and_imported_models(self):
        program = CouplingRunningConvergenceProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))
        certificate = formal_certificate()
        self.assertTrue(all(item["gap_below_tolerance"] for item in certificate["convergence_witnesses"]))
        translation = carrier_translation_record()
        self.assertFalse(translation["measurement_selects_orientation"])
        source = (
            ROOT / "sft/physics/coupling_running_convergence_terminal_law_v1.py"
        ).read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("expected_survivor", lowered)
        self.assertNotIn('"admitted": true', lowered)
        self.assertNotIn("fraction(0", lowered)
        self.assertNotIn("0.1180", lowered)
        self.assertNotIn("137.035", lowered)


if __name__ == "__main__":
    unittest.main()
