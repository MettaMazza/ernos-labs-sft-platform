"""Checks for the minimal structural Fold."""

from dataclasses import replace
import importlib.util
import unittest

from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.fold import CLAIM_ID, candidate_records


def load_execution():
    path = ROOT / "claims" / CLAIM_ID / "execution.py"
    specification = importlib.util.spec_from_file_location("fold_test_execution", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


class FoldTests(unittest.TestCase):
    def test_complete_fold_grammar_has_288_generated_forms(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        self.assertEqual(census.expected_cardinality, len(candidate_records()))
        self.assertEqual(len(census.candidates), 288)

    def test_first_equal_distinct_returning_form_is_the_only_survivor(self):
        execution = load_execution()
        census = execution.program.generate_candidates()
        decisions = tuple(
            execution.program.decide_candidate(item) for item in census.candidates
        )
        self.assertEqual(
            [item.candidate_id for item in decisions if item.survives],
            [
                "complete__disjoint__equal__first-extension__labels-distinct-held__"
                "return-present__no-extra"
            ],
        )
        self.assertTrue(all(item.passed for item in execution.program.run_controls()))

    def test_fold_executes_from_one_count_and_part(self):
        execution = load_execution()
        receipt = EngineRepository(ROOT).engine.run(
            execution.program, execution.independent_validator
        )
        self.assertTrue(receipt.model_admitted)
        self.assertEqual(receipt.closure_status, "depth_independent")

    def test_independent_validator_rejects_a_later_extension_survivor(self):
        execution = load_execution()
        captured = {}

        class Capture:
            def validate(self, sealed):
                captured["sealed"] = sealed
                return execution.independent_validator.validate(sealed)

        EngineRepository(ROOT).engine.run(execution.program, Capture())
        sealed = captured["sealed"]
        candidate = (
            "complete__disjoint__equal__later-extension__labels-distinct-held__"
            "return-present__no-extra"
        )
        index = next(
            index
            for index, decision in enumerate(sealed.decisions)
            if decision.candidate_id == candidate
        )
        decisions = list(sealed.decisions)
        decisions[index] = replace(decisions[index], survives=True)
        self.assertFalse(
            execution.independent_validator.validate(
                replace(sealed, decisions=tuple(decisions))
            ).passed
        )


if __name__ == "__main__":
    unittest.main()
