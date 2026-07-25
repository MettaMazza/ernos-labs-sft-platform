from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.physics.odd_lattice_all_region_terminal_law_v1 import (
    OddLatticeAllRegionProgram,
    candidate_forms,
    formal_certificate,
    form_survives,
    occupancy_invariance_certificate,
    occupancy_vector,
    permutation_certificate,
)
from sft.physics.odd_lattice_all_region_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
    experiment_registration_record,
)


ROOT = Path(__file__).resolve().parents[1]


class OddLatticeAllRegionTerminalTests(unittest.TestCase):
    def test_general_odd_lattice_permutation_and_depth_invariance(self) -> None:
        for members, regions in ((3, 2), (5, 3), (7, 4), (9, 5), (15, 8), (31, 17)):
            self.assertTrue(permutation_certificate(members)["image_is_complete_support"])
            certificate = occupancy_invariance_certificate(members, regions, members)
            self.assertTrue(certificate["all_steps_equal"])
            self.assertTrue(certificate["all_regions_occupied"])
            self.assertTrue(certificate["total_members_retained"])

    def test_complete_candidate_product_has_one_computed_survivor(self) -> None:
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2916)
        self.assertEqual(len({form.candidate_id for form in forms}), 2916)
        self.assertEqual(len(survivors), 1)
        self.assertNotIn("target-assigned", survivors[0].candidate_id)

    def test_formal_claim_has_no_historical_target_or_answer_key(self) -> None:
        path = ROOT / "sft/physics/odd_lattice_all_region_terminal_law_v1.py"
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "SFTOM-V1",
            "source-record",
            "expected_survivor",
            '"admitted": true',
            "D.even_lattice(255)",
            "(255, 12, 8)",
            "(32, 32, 32, 32, 32, 32, 32, 31)",
        ):
            self.assertNotIn(forbidden, text)
        self.assertTrue(all(item["all_steps_equal"] for item in formal_certificate()["certificates"]))

    def test_postseal_replication_retains_complete_vector(self) -> None:
        target = authoritative_record(ROOT)["registered_target"]
        analysis = exact_measurement_analysis(target)
        self.assertEqual(analysis["complete_recurrence_vector"], (32, 32, 32, 32, 32, 32, 32, 31))
        self.assertTrue(analysis["depth_invariant"])
        self.assertTrue(analysis["all_regions_occupied"])
        self.assertTrue(analysis["complete_member_total_retained"])
        self.assertTrue(analysis["exact_balance_span_is_One"])

    def test_registration_is_machine_reproducible(self) -> None:
        registration = experiment_registration_record()
        encoded = json.loads(json.dumps(registration))
        self.assertEqual(encoded["claim_id"], "SFT-PHYS-ODD-LATTICE-ALL-REGION-OCCUPANCY-TERMINAL-007")
        self.assertEqual(len(encoded["source_hashes"]), 3)
        self.assertEqual(len(encoded["withheld_target_ids"]), 1)
        program = OddLatticeAllRegionProgram("sha256:test-source")
        census = program.generate_candidates()
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertTrue(program.closure_evidence(decisions).minimality_passed)
        self.assertTrue(all(control.passed for control in program.run_controls()))


if __name__ == "__main__":
    unittest.main()
