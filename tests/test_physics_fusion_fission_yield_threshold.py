from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.fusion_fission_yield_threshold_law_v1 import (
    FusionFissionYieldThresholdProgram,
    candidate_forms,
    exact_release_order,
    form_survives,
    threshold_topology,
)
from sft.physics.fusion_fission_yield_threshold_validation_v1 import (
    TARGET_IDS,
    authoritative_record,
    exact_binding_measurement_analysis,
    iaea_measurement_analysis,
    released_targets,
)


ROOT = Path(__file__).resolve().parents[1]


class FusionFissionYieldThresholdTests(unittest.TestCase):
    def test_complete_product_has_one_computed_form(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 5832)
        self.assertEqual(len({form.candidate_id for form in forms}), 5832)
        self.assertEqual(len(survivors), 1)
        self.assertEqual(survivors[0].per_nucleon_relation, "fusion-greater-per-nucleon")
        self.assertEqual(survivors[0].total_release_relation, "fission-greater-total")

    def test_exact_formal_orders_are_strict_and_metrics_are_not_conflated(self):
        order = exact_release_order()
        self.assertTrue(order["fusion_greater_per_nucleon"])
        self.assertTrue(order["fission_greater_total"])
        self.assertGreater(
            order["fusion_per_nucleon"][0], order["fission_per_nucleon"][1]
        )
        self.assertGreater(order["fission_total"][0], order["fusion_total"][1])
        for interval in (
            order["fusion_per_nucleon"],
            order["fission_per_nucleon"],
            order["fusion_total"],
            order["fission_total"],
        ):
            self.assertIsInstance(interval[0], Fraction)
            self.assertGreater(interval[0], 0)

    def test_threshold_carriers_are_structurally_distinct(self):
        topology = threshold_topology()
        self.assertTrue(topology["fusion_has_two_charged_incident_words"])
        self.assertEqual(topology["fusion_inter_boundary_paths"], 1)
        self.assertTrue(topology["fission_has_one_parent_word"])
        self.assertEqual(topology["fission_inter_boundary_paths"], ())
        self.assertTrue(topology["neutral_trigger_charge_is_empty_form"])
        self.assertTrue(topology["internal_surface_is_finite"])
        self.assertTrue(topology["carriers_are_distinct"])

    def test_complete_external_comparison_preserves_energy_and_threshold_rows(self):
        record = authoritative_record(ROOT)
        targets = released_targets(ROOT)
        binding = exact_binding_measurement_analysis(targets[TARGET_IDS[0]])
        iaea = iaea_measurement_analysis(
            targets[TARGET_IDS[2]], targets[TARGET_IDS[3]], targets[TARGET_IDS[4]]
        )
        self.assertEqual(len(record["sources"]), 5)
        self.assertEqual(len(targets[TARGET_IDS[0]]), 2548)
        self.assertEqual(len(targets[TARGET_IDS[2]]), 12)
        self.assertEqual(len(targets[TARGET_IDS[3]]["component_rows"]), 7)
        self.assertTrue(binding["fusion_greater_per_nucleon"])
        self.assertTrue(binding["fission_greater_total"])
        self.assertTrue(iaea["fusion_greater_per_nucleon"])
        self.assertTrue(iaea["fission_greater_total"])
        self.assertTrue(iaea["threshold_classes_complete"])
        self.assertTrue(iaea["charged_clause_retains_true_vs_effective_threshold"])
        self.assertTrue(iaea["neutral_fission_scope_retained"])

    def test_controls_are_computed_and_formal_module_has_no_target_reader_or_answer_key(self):
        program = FusionFissionYieldThresholdProgram("sha256:" + "1" * 64)
        controls = program.run_controls()
        self.assertEqual(
            {control.kind.value for control in controls},
            {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        )
        self.assertTrue(all(control.passed for control in controls))
        source = (
            ROOT / "sft/physics/fusion_fission_yield_threshold_law_v1.py"
        ).read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("source_record_path", lowered)
        self.assertNotIn("read_text(", lowered)
        self.assertNotIn("survivor = \"", source)
        self.assertNotIn('"admitted": true', lowered)


if __name__ == "__main__":
    unittest.main()
