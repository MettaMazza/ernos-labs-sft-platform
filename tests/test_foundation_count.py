"""Checks for exact positive finite count."""

from dataclasses import replace
import importlib.util
import unittest

from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.count import CLAIM_ID, candidate_records


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    specification = importlib.util.spec_from_file_location("count_test_execution", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


class PositiveCountTests(unittest.TestCase):
    def test_complete_representation_grammar_has_ten_generated_forms(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        self.assertEqual(census.expected_cardinality, len(candidate_records()))
        self.assertEqual(len(census.candidates), 10)

    def test_complete_once_no_extra_is_the_only_survivor(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        decisions = tuple(
            execution.program.decide_candidate(item) for item in census.candidates
        )
        self.assertEqual(
            [item.candidate_id for item in decisions if item.survives],
            ["complete-coverage__once__no-extra"],
        )
        self.assertTrue(all(item.passed for item in execution.program.run_controls()))

    def test_count_executes_only_from_the_admitted_structural_one(self):
        execution = load_execution()
        repository = EngineRepository(ROOT)
        receipt = repository.engine.run(
            execution.program, execution.independent_validator
        )
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.closure_status, "depth_independent")

    def test_independent_validator_rejects_a_tampered_duplicate_survivor(self):
        execution = load_execution()
        captured = {}

        class Capture:
            def validate(self, sealed):
                captured["sealed"] = sealed
                return execution.independent_validator.validate(sealed)

        EngineRepository(ROOT).engine.run(execution.program, Capture())
        sealed = captured["sealed"]
        duplicate_index = next(
            index
            for index, decision in enumerate(sealed.decisions)
            if decision.candidate_id == "complete-coverage__duplicated__no-extra"
        )
        altered = list(sealed.decisions)
        altered[duplicate_index] = replace(
            altered[duplicate_index], survives=True
        )
        tampered = replace(sealed, decisions=tuple(altered))
        self.assertFalse(execution.independent_validator.validate(tampered).passed)


if __name__ == "__main__":
    unittest.main()
