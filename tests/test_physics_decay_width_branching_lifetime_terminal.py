from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.decay_width_branching_lifetime_terminal_law_v1 import (
    DecayWidthBranchingLifetimeProgram,
    append_open_channel,
    branching_parts,
    candidate_forms,
    closed_channel,
    complete_branching_partition,
    formal_certificate,
    form_survives,
    lifetime_from_width,
    partial_transition_width,
    sample_partial_widths,
    successor_total_increment,
    total_transition_width,
    wider_state_lifetime_take,
)
from sft.physics.decay_width_branching_lifetime_terminal_validation_v1 import (
    authoritative_record,
    codata_action_row,
    exact_measurement_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class DecayWidthBranchingLifetimeTerminalTests(unittest.TestCase):
    def test_complete_product_has_one_computed_form(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 8748)
        self.assertEqual(len({form.candidate_id for form in forms}), 8748)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(
            survivors[0].total_width_law,
            "ordered-positive-sum-of-partial-widths",
        )
        self.assertEqual(
            survivors[0].branching_law,
            "partial-width-over-total-width",
        )
        self.assertEqual(survivors[0].lifetime_law, "action-over-total-width")

    def test_exact_partial_total_branch_and_lifetime_laws(self):
        widths = sample_partial_widths()
        self.assertEqual(
            widths,
            (Fraction(1, 4), Fraction(1, 2), Fraction(5, 4)),
        )
        self.assertEqual(
            partial_transition_width(Fraction(1, 2), Fraction(3, 4), Fraction(1, 1)),
            Fraction(3, 16),
        )
        self.assertEqual(total_transition_width(widths), Fraction(2, 1))
        self.assertEqual(
            branching_parts(widths),
            (Fraction(1, 8), Fraction(1, 4), Fraction(5, 8)),
        )
        self.assertEqual(complete_branching_partition(widths), Fraction(1, 1))
        self.assertEqual(lifetime_from_width(Fraction(1, 1), Fraction(2, 1)), Fraction(1, 2))
        self.assertEqual(closed_channel(), ())

    def test_channel_successor_preserves_partition_and_inverse_ordering(self):
        widths = sample_partial_widths()
        for successor in (
            Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1)
        ):
            enlarged = append_open_channel(widths, successor)
            self.assertEqual(successor_total_increment(widths, successor), successor)
            self.assertEqual(complete_branching_partition(enlarged), Fraction(1, 1))
        self.assertGreater(
            wider_state_lifetime_take(
                Fraction(1, 1), Fraction(1, 2), Fraction(2, 1)
            ),
            0,
        )

    def test_complete_pdg_nist_comparison_closes_declared_values(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(ROOT)
        self.assertEqual(len(record["sources"]), 2)
        self.assertEqual(analysis["pdg"]["width_row_count"], 16)
        self.assertEqual(analysis["pdg"]["mode_row_count"], 13)
        self.assertEqual(analysis["pdg"]["individual_exclusive_row_count"], 4)
        self.assertTrue(analysis["pdg"]["published_exact_complement_relation"])
        self.assertTrue(analysis["pdg"]["universal_interval_contains_one"])
        self.assertTrue(
            analysis["pdg"]["forced_universal_hadron_inside_reported_interval"]
        )
        self.assertTrue(analysis["pdg"]["individual_interval_contains_one"])
        self.assertTrue(
            analysis["pdg"]["forced_individual_hadron_inside_reported_interval"]
        )
        self.assertTrue(
            analysis["pdg"]["partial_width_sum_encloses_total_width_interval"]
        )
        self.assertTrue(analysis["pdg"]["subsets_retained_without_double_counting"])
        self.assertTrue(analysis["nist"]["finite_positive_lifetime_interval"])
        self.assertTrue(analysis["nist"]["greater_width_shorter_lifetime"])
        self.assertIn("6.582 119 569... e-16", codata_action_row(ROOT))

    def test_controls_and_formal_source_exclude_targets_answers_and_numeric_null(self):
        program = DecayWidthBranchingLifetimeProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))
        certificate = formal_certificate()
        self.assertEqual(certificate["closed_channel"], ())
        source = (
            ROOT / "sft/physics/decay_width_branching_lifetime_terminal_law_v1.py"
        ).read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("expected_survivor", lowered)
        self.assertNotIn('"admitted": true', lowered)
        self.assertNotIn("fraction(0", lowered)


if __name__ == "__main__":
    unittest.main()
