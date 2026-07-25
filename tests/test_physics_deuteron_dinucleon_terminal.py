from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.deuteron_dinucleon_terminal_law_v1 import (
    ALTERNATING,
    PRESERVING,
    DeuteronDinucleonProgram,
    binding_outcomes,
    candidate_forms,
    composite_spin_certificate,
    exchange_partition,
    form_survives,
    pair_channels,
)
from sft.physics.deuteron_dinucleon_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
)


ROOT = Path(__file__).resolve().parents[1]


class DeuteronDinucleonTerminalTests(unittest.TestCase):
    def test_complete_product_has_one_computed_form(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2592)
        self.assertEqual(len({form.candidate_id for form in forms}), 2592)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0].binding_table, "pn-only-bound")
        self.assertEqual(
            survivors[0].composite_spin,
            "complete-One-with-three-readings",
        )

    def test_exchange_support_and_residual_remainder_are_exact(self):
        partition = exchange_partition()
        certificate = composite_spin_certificate()
        self.assertEqual(len(partition[PRESERVING]), 3)
        self.assertEqual(len(partition[ALTERNATING]), 1)
        self.assertEqual(certificate["preserving_support"], Fraction(3, 4))
        self.assertEqual(certificate["alternating_support"], Fraction(1, 4))
        self.assertEqual(certificate["residual_boundary"], Fraction(1, 4))
        self.assertEqual(certificate["preserving_remainder"], Fraction(1, 2))
        self.assertEqual(certificate["alternating_remainder"], ())
        self.assertEqual(certificate["preserving_composite_spin"], Fraction(1, 1))

    def test_complete_exchange_ledger_forces_pn_only_binding(self):
        rows = {row.pair_class: row for row in pair_channels()}
        self.assertEqual(
            binding_outcomes(),
            {
                "proton-neutron": True,
                "proton-proton": False,
                "neutron-neutron": False,
            },
        )
        self.assertEqual(rows["proton-neutron"].spin_hand, PRESERVING)
        self.assertEqual(rows["proton-proton"].spin_hand, ALTERNATING)
        self.assertEqual(rows["neutron-neutron"].spin_hand, ALTERNATING)
        self.assertEqual(rows["proton-proton"].charge_path, Fraction(1, 1))
        self.assertEqual(rows["neutron-neutron"].charge_path, ())

    def test_complete_external_comparison_closes_spin_inventory_and_value(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(ROOT)
        self.assertEqual(len(record["sources"]), 5)
        self.assertEqual(analysis["ame"]["complete_coordinate_count"], 3558)
        self.assertEqual(analysis["nubase"]["complete_state_count"], 5843)
        self.assertTrue(analysis["complete_a2_inventory_is_deuteron_only"])
        self.assertTrue(
            analysis["nubase"]["directly_measured_spin_one_positive_parity"]
        )
        self.assertTrue(analysis["codata_ame_binding_intervals_overlap"])
        self.assertTrue(
            analysis["iaea"]["all_singlet_triplet_rows_sign_separated"]
        )
        self.assertTrue(analysis["iaea"]["parallel_bound_deuteron_recorded"])

    def test_controls_are_computed_and_formal_module_has_no_target_or_answer_key(self):
        program = DeuteronDinucleonProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))
        source = (
            ROOT / "sft/physics/deuteron_dinucleon_terminal_law_v1.py"
        ).read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("survivor = \"", source)
        self.assertNotIn('"admitted": true', lowered)


if __name__ == "__main__":
    unittest.main()
