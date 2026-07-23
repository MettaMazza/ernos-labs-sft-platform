"""Checks for the independently derived structural One."""

from dataclasses import replace
import importlib.util
import unittest

from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.one import CLAIM_ID, candidate_records


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    specification = importlib.util.spec_from_file_location("one_test_execution", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


class StructuralOneTests(unittest.TestCase):
    def test_complete_coverage_product_has_six_generated_forms(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        self.assertEqual(census.expected_cardinality, len(candidate_records()))
        self.assertEqual(len(census.candidates), 6)

    def test_exact_self_whole_is_the_only_survivor(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        decisions = tuple(execution.program.decide_candidate(item) for item in census.candidates)
        self.assertEqual(
            [item.candidate_id for item in decisions if item.survives],
            ["exact-self-whole"],
        )
        self.assertTrue(all(item.passed for item in execution.program.run_controls()))

    def test_one_executes_with_only_the_admitted_root_dependency(self):
        execution = load_execution()
        repository = EngineRepository(ROOT)
        receipt = repository.engine.run(execution.program, execution.independent_validator)
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.closure_status, "depth_independent")

    def test_independent_validator_rejects_tampered_extra_survivor(self):
        execution = load_execution()
        captured = {}

        class Capture:
            def validate(self, sealed):
                captured["sealed"] = sealed
                return execution.independent_validator.validate(sealed)

        EngineRepository(ROOT).engine.run(execution.program, Capture())
        sealed = captured["sealed"]
        tampered = replace(
            sealed,
            decisions=(replace(sealed.decisions[0], survives=True), *sealed.decisions[1:]),
        )
        self.assertFalse(execution.independent_validator.validate(tampered).passed)


if __name__ == "__main__":
    unittest.main()
