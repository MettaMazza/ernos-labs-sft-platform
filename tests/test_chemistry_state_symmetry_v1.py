from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.state_symmetry_law_v1 import (
    FiniteStateEquivalenceClass,
    StateSymmetrySignature,
    axis_rank_from_source_symbol,
    build_equivalence_class,
    equivalent,
    symmetry_signature_from_source,
)
from sft.chemistry.state_symmetry_validation_v1 import (
    StateSymmetryValidator,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, FoldWord, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class StateSymmetryTests(unittest.TestCase):
    def test_axis_rank_uses_empty_one_then_positive_recurrence(self):
        self.assertEqual(axis_rank_from_source_symbol("Σ"), EMPTY_ONE)
        self.assertEqual(axis_rank_from_source_symbol("Π"), PositiveCount(1))
        self.assertEqual(axis_rank_from_source_symbol("Δ"), PositiveCount(2))
        self.assertEqual(axis_rank_from_source_symbol("Φ"), PositiveCount(3))

    def test_positive_degeneracy_is_forced_product(self):
        sigma = symmetry_signature_from_source(
            "H2", PositiveCount(1), "Σ", "g", "plus-fibre", "absence", "absence"
        )
        pi = symmetry_signature_from_source(
            "NO", PositiveCount(2), "Π", "absence", "absence", "absence", "r"
        )
        self.assertEqual(build_equivalence_class(sigma).signature.positive_degeneracy_count, PositiveCount(1))
        self.assertEqual(build_equivalence_class(pi).signature.positive_degeneracy_count, PositiveCount(4))

    def test_complete_signature_controls_equivalence(self):
        first = symmetry_signature_from_source(
            "m", PositiveCount(1), "Σ", "absence", "plus-fibre", "absence", "absence"
        )
        same = symmetry_signature_from_source(
            "m", PositiveCount(1), "Σ", "absence", "plus-fibre", "absence", "absence"
        )
        changed = symmetry_signature_from_source(
            "m", PositiveCount(1), "Σ", "absence", "minus-fibre", "absence", "absence"
        )
        self.assertTrue(equivalent(first, same))
        self.assertFalse(equivalent(first, changed))

    def test_wrong_orientation_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            StateSymmetrySignature(
                HeldLabel("molecular-carrier", "m"),
                PositiveCount(1),
                EMPTY_ONE,
                PositiveCount(2),
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
                EMPTY_ONE,
            )

    def test_incomplete_component_class_halts(self):
        signature = symmetry_signature_from_source(
            "m", PositiveCount(2), "Π", "absence", "absence", "absence", "absence"
        )
        with self.assertRaises(InadmissibleExactValue):
            FiniteStateEquivalenceClass(
                signature,
                (HeldLabel("state-component", "only-one"),),
            )

    def test_absence_is_empty_one_and_numeric_zero_halts(self):
        signature = symmetry_signature_from_source(
            "m", PositiveCount(1), "Σ", "absence", "absence", "absence", "absence"
        )
        self.assertEqual(signature.axis_rank, EMPTY_ONE)
        self.assertEqual(signature.inversion_label, EMPTY_ONE)
        self.assertEqual(signature.axis_component, EMPTY_ONE)
        with self.assertRaises(FoldLanguageHalt):
            FoldWord((0,))

    def test_capability_closed_prediction_contains_only_universal_law(self):
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(prediction_program_document(ROOT)),
            {"registered-premise": HeldLabel("sealed-derivation", "unit")},
        )
        self.assertIsInstance(execution.output, FoldTable)
        self.assertEqual(len(execution.output.entries), 12)

    def test_complete_nist_symmetry_vector(self):
        result = StateSymmetryValidator(ROOT).validate(
            SimpleNamespace(seal_hash="sha256:" + "e" * 64)
        )
        self.assertTrue(result.passed)
        self.assertEqual(len(result.measurements), 379)


if __name__ == "__main__":
    unittest.main()
