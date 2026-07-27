from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.joint_correlation_law_v1 import (
    JointSeparatedPairSupport,
    complete_separated_pair_support,
    dissociation_observation,
)
from sft.chemistry.joint_correlation_validation_v1 import (
    JointCorrelationValidator,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, FoldWord, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class JointCorrelationTests(unittest.TestCase):
    def test_complete_joint_support_is_two_against_four(self):
        support = complete_separated_pair_support("H2", "left", "right")
        self.assertEqual(support.positive_joint_word_count, PositiveCount(2))
        self.assertEqual(support.positive_independent_cartesian_count, PositiveCount(4))
        self.assertTrue(support.retains_nonfactorizable_joint_distinction)

    def test_incomplete_joint_support_halts(self):
        support = complete_separated_pair_support("H2", "left", "right")
        with self.assertRaises(InadmissibleExactValue):
            JointSeparatedPairSupport(support.molecular_carrier, support.left_centre, support.right_centre, support.joint_words[:1])

    def test_factorized_four_word_support_halts(self):
        support = complete_separated_pair_support("H2", "left", "right")
        extra = FoldWord((HeldLabel("electron-held-fibre", "lower-fibre"), support.left_centre, HeldLabel("electron-held-fibre", "upper-fibre"), support.left_centre))
        with self.assertRaises(InadmissibleExactValue):
            JointSeparatedPairSupport(support.molecular_carrier, support.left_centre, support.right_centre, support.joint_words + (extra,))

    def test_same_centre_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            complete_separated_pair_support("H2", "same", "same")

    def test_positive_dissociation_observation(self):
        observation = dissociation_observation("APS", "H2", "X", "bound-to-products", 3611811, 100, 8, 100)
        self.assertEqual(observation.positive_energy_separation.numerator.value, 3611811)

    def test_absent_uncertainty_is_empty_one(self):
        observation = dissociation_observation("NIST", "H2", "B", "bound-to-products", 281742, 10, "absence", "absence")
        self.assertIs(observation.positive_uncertainty_or_absence, EMPTY_ONE)

    def test_numeric_zero_halts(self):
        with self.assertRaises(FoldLanguageHalt):
            FoldWord((0,))

    def test_capability_closed_prediction_contains_only_universal_law(self):
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(prediction_program_document(ROOT)),
            {"registered-premise": HeldLabel("sealed-derivation", "unit")},
        )
        self.assertIsInstance(execution.output, FoldTable)
        self.assertEqual(len(execution.output.entries), 5)

    def test_complete_dissociation_vector(self):
        result = JointCorrelationValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "e" * 64))
        self.assertTrue(result.passed)
        self.assertEqual(len(result.measurements), 30)


if __name__ == "__main__":
    unittest.main()
