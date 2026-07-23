"""Unit and end-to-end checks for the premise-free v3 root theorem."""

from dataclasses import replace
import importlib.util
import unittest

from sft.cli import ROOT
from sft.engine import ROOT_THEOREM, SFTAdmissionEngine
from sft.foundation.root_theorem import candidate_records


def load_execution():
    path = ROOT / "claims" / ROOT_THEOREM / "execution.py"
    specification = importlib.util.spec_from_file_location("root_theorem_test_execution", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


class RootTheoremTests(unittest.TestCase):
    def test_root_registration_has_no_premise_axiom_parameter_or_dependency(self):
        registration = load_execution().program.registration
        self.assertEqual(registration.claim_id, ROOT_THEOREM)
        self.assertEqual(registration.root_theorems, ())
        self.assertEqual(registration.dependencies, ())
        self.assertEqual(registration.axioms, ())
        self.assertEqual(registration.free_parameters, ())

    def test_complete_operational_partition_has_one_survivor(self):
        execution = load_execution()
        program = execution.program
        census = program.generate_candidates()
        self.assertEqual(census.expected_cardinality, len(candidate_records()))
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertEqual([item.survives for item in decisions], [False, True])
        closure = program.closure_evidence(decisions)
        self.assertEqual(closure.scope.value, "depth_independent")
        self.assertTrue(all(control.passed for control in program.run_controls()))

    def test_root_executes_end_to_end_through_independent_validator(self):
        execution = load_execution()
        receipt = SFTAdmissionEngine().run(execution.program, execution.independent_validator)
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.external_status, "independently_replicated")

    def test_independent_validator_rejects_a_tampered_survivor(self):
        execution = load_execution()
        captured = {}

        class Capture:
            def validate(self, sealed):
                captured["sealed"] = sealed
                return execution.independent_validator.validate(sealed)

        SFTAdmissionEngine().run(execution.program, Capture())
        sealed = captured["sealed"]
        tampered_first = replace(sealed.decisions[0], survives=True)
        tampered = replace(sealed, decisions=(tampered_first, *sealed.decisions[1:]))
        validation = execution.independent_validator.validate(tampered)
        self.assertFalse(validation.passed)


if __name__ == "__main__":
    unittest.main()
