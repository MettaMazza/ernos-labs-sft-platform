"""Formal and operational checks for the Physics empirical prerequisites."""

import unittest

from sft.engine import ControlKind
from sft.physics.formal_law import FormalPrerequisiteProgram, candidate_rows, survivor_id
from sft.physics.measurement_prerequisites import PREREQUISITE_SPECS


class PhysicsPrerequisiteTests(unittest.TestCase):
    def test_catalog_is_dependency_ordered_and_witnessed(self) -> None:
        available = {
            dependency
            for spec in PREREQUISITE_SPECS
            for dependency in spec.dependencies
            if not dependency.startswith("SFT-PHYS-MEAS-")
        }
        self.assertEqual(len(PREREQUISITE_SPECS), 3)
        for spec in PREREQUISITE_SPECS:
            self.assertTrue(all(witness.passed for witness in spec.witnesses))
            self.assertFalse(tuple(dependency for dependency in spec.dependencies if dependency not in available))
            available.add(spec.claim_id)

    def test_each_registered_product_is_complete_and_unique(self) -> None:
        for spec in PREREQUISITE_SPECS:
            with self.subTest(claim_id=spec.claim_id):
                rows = candidate_rows(spec)
                self.assertEqual(len(rows), 256)
                self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
                self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)

    def test_program_decisions_closure_and_controls(self) -> None:
        for spec in PREREQUISITE_SPECS:
            with self.subTest(claim_id=spec.claim_id):
                program = FormalPrerequisiteProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
                self.assertEqual(sum(decision.survives for decision in decisions), 1)
                closure = program.closure_evidence(decisions)
                self.assertTrue(closure.minimality_passed)
                self.assertTrue(closure.named_shape_uniqueness_passed)
                controls = program.run_controls()
                self.assertEqual({control.kind for control in controls}, set(ControlKind))
                self.assertTrue(all(control.passed for control in controls))


if __name__ == "__main__":
    unittest.main()
