from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.fusion_fission_terminal_law_v1 import (
    FusionFissionTerminalProgram,
    binding_gain_enclosure,
    candidate_forms,
    fission_trace,
    form_survives,
    fusion_trace,
    reaction_conserves_counts,
)
from sft.physics.fusion_fission_terminal_validation_v1 import (
    measured_binding_rows,
    measurement_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class FusionFissionTerminalTests(unittest.TestCase):
    def test_complete_candidate_product_has_one_computed_survivor(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 1152)
        self.assertEqual(len({form.candidate_id for form in forms}), 1152)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0].fusion_operation, "binary-junction")
        self.assertEqual(survivors[0].fission_operation, "binary-decomposition")
        self.assertEqual(survivors[0].barrier_label, "half-One")

    def test_exact_reaction_counts_and_binding_gains_are_positive(self):
        fusion = fusion_trace("binary-junction")
        fission = fission_trace("binary-decomposition")
        self.assertTrue(reaction_conserves_counts(fusion))
        self.assertTrue(reaction_conserves_counts(fission))
        for gain in (binding_gain_enclosure(fusion), binding_gain_enclosure(fission)):
            self.assertNotEqual(gain, ())
            self.assertIsInstance(gain[0], Fraction)
            self.assertGreater(gain[0], 0)
            self.assertGreaterEqual(gain[1], gain[0])

    def test_controls_are_computed_and_all_required_kinds_pass(self):
        program = FusionFissionTerminalProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))

    def test_complete_ame2020_comparison_retains_both_directions_and_controls(self):
        rows = measured_binding_rows(ROOT)
        analysis = measurement_analysis(rows)
        self.assertEqual(analysis["row_count"], 2548)
        self.assertTrue(analysis["fusion_higher_after_uncertainty"])
        self.assertTrue(analysis["fission_higher_after_uncertainty"])
        self.assertTrue(analysis["peak_separated_from_every_rival"])
        self.assertTrue(analysis["reversed_fusion_rejected"])
        self.assertTrue(analysis["reversed_fission_rejected"])

    def test_formal_module_contains_no_target_reader_or_answer_flag(self):
        source = (ROOT / "sft/physics/fusion_fission_terminal_law_v1.py").read_text(
            encoding="utf-8"
        )
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("survivor = \"", source)
        self.assertNotIn('"admitted": true', lowered)


if __name__ == "__main__":
    unittest.main()
