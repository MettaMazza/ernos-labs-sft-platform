"""Unit and integration checks for Reversible and Quantum Computation."""
from __future__ import annotations
import unittest
from sft.quantum_computation.catalog import SPECS, validate_catalog
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, candidate_records, survivor_id
from sft.quantum_computation.operations import FoldQuantumState, ReversibleGate, apply_gate, complete_support, exhaustive_fault_census, is_factorable, observe, repetition_encode

class QuantumCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_unique_and_ordered(self) -> None:
        validate_catalog()
        self.assertEqual(len(SPECS), 21)
        self.assertEqual(len({spec.claim_id for spec in SPECS}), 21)

    def test_every_claim_has_one_survivor_and_live_witnesses(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                program = GeneratedQuantumProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                survivor = next(candidate for candidate in census.candidates if candidate.candidate_id == survivor_id(spec))
                self.assertTrue(program.decide_candidate(survivor).survives)
                self.assertFalse(program.decide_candidate(census.candidates[0]).survives)
                self.assertTrue(all(control.passed for control in program.run_controls()))
                self.assertTrue(all(witness.passed for witness in spec.witnesses))

class QuantumOperationalTests(unittest.TestCase):
    def test_entangled_support_is_not_factorable(self) -> None:
        self.assertFalse(is_factorable((("held", "held"), ("returned", "returned"))))
        self.assertTrue(is_factorable((("held", "held"), ("held", "returned"), ("returned", "held"), ("returned", "returned"))))

    def test_measurement_requires_complete_observation(self) -> None:
        state = complete_support(("held", "returned"), ("p1",), ("phase-held", "phase-returned"))
        with self.assertRaises(ValueError):
            observe(state, ((("held",), "left"),), "left")

    def test_reversible_gate_rejects_nonbijection(self) -> None:
        with self.assertRaises(ValueError):
            ReversibleGate(((("held",), ("held",)), (("returned",), ("held",))), ("phase-step",))

    def test_multi_error_census_corrects_widths_three_five_seven(self) -> None:
        expected_rows = {1: 4, 2: 16, 3: 64}
        for depth in (1, 2, 3):
            trace = tuple(f"fault-{index + 1}" for index in range(depth))
            census = exhaustive_fault_census("held", trace)
            self.assertEqual(len(census), expected_rows[depth])
            self.assertTrue(all(decoded == "held" for _word, decoded in census))
            self.assertEqual(len(repetition_encode("held", trace)), 2 * depth + 1)

    def test_state_rejects_duplicate_branch(self) -> None:
        with self.assertRaises(ValueError):
            FoldQuantumState(((("held",), "p"), (("held",), "q")), ("p", "q"))

if __name__ == "__main__":
    unittest.main()
