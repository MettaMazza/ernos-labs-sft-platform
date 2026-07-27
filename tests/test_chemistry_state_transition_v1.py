from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.state_transition_law_v1 import BIDIRECTIONAL, FORWARD, absent_transition, compose_transition_path, observed_transition
from sft.chemistry.state_transition_validation_v1 import StateTransitionValidator, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, FoldWord, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine.exact import HeldLabel, InadmissibleExactValue


ROOT = Path(__file__).resolve().parents[1]


class StateTransitionTests(unittest.TestCase):
    def test_observed_transition_retains_endpoints(self):
        row = observed_transition("H2", "B", "X", BIDIRECTIONAL, "B-X")
        self.assertTrue(row.is_observed); self.assertNotEqual(row.initial_state, row.terminal_state_or_absence)
    def test_absent_transition_uses_empty_one(self):
        row = absent_transition("H2", "X", "source-absence")
        self.assertIs(row.terminal_state_or_absence, EMPTY_ONE); self.assertFalse(row.is_observed)
    def test_matching_path_composes(self):
        path = compose_transition_path(observed_transition("H2", "A", "B", FORWARD, "A-B"), observed_transition("H2", "B", "C", FORWARD, "B-C"))
        self.assertEqual(len(path.cells), 6)
    def test_mismatched_path_halts(self):
        with self.assertRaises(InadmissibleExactValue): compose_transition_path(observed_transition("H2", "A", "B", FORWARD, "A-B"), observed_transition("H2", "C", "D", FORWARD, "C-D"))
    def test_self_transition_halts(self):
        with self.assertRaises(InadmissibleExactValue): observed_transition("H2", "A", "A", FORWARD, "invalid")
    def test_absent_path_halts(self):
        with self.assertRaises(InadmissibleExactValue): compose_transition_path(absent_transition("H2", "A", "absence"), observed_transition("H2", "A", "B", FORWARD, "A-B"))
    def test_numeric_zero_halts(self):
        with self.assertRaises(FoldLanguageHalt): FoldWord((0,))
    def test_capability_closed_prediction_is_universal_only(self):
        execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(prediction_program_document(ROOT)), {"registered-premise": HeldLabel("sealed-derivation", "unit")})
        self.assertIsInstance(execution.output, FoldTable); self.assertEqual(len(execution.output.entries), 9)
    def test_complete_nist_transition_vector(self):
        result = StateTransitionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "e" * 64))
        self.assertTrue(result.passed); self.assertEqual(len(result.measurements), 80)


if __name__ == "__main__": unittest.main()
