from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.pair_exchange_law_v1 import (
    ALTERNATING_EXCHANGE,
    PRESERVING_EXCHANGE,
    SAME_CELL_ADMITTED,
    SAME_CELL_EXCLUDED,
    MolecularElectronPairState,
    build_same_support_pair,
    exchange_product,
    explicit_occupancy_compatible,
    pair_state_from_multiplicity,
)
from sft.chemistry.pair_exchange_validation_v1 import (
    PairExchangeValidator,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, FoldWord, fold_program_from_mapping
from sft.claim_evidence.fold_language import FoldLanguageHalt
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class PairExchangeTests(unittest.TestCase):
    def test_complete_exchange_product(self):
        self.assertEqual(exchange_product(PRESERVING_EXCHANGE, PRESERVING_EXCHANGE), PRESERVING_EXCHANGE)
        self.assertEqual(exchange_product(PRESERVING_EXCHANGE, ALTERNATING_EXCHANGE), ALTERNATING_EXCHANGE)
        self.assertEqual(exchange_product(ALTERNATING_EXCHANGE, PRESERVING_EXCHANGE), ALTERNATING_EXCHANGE)
        self.assertEqual(exchange_product(ALTERNATING_EXCHANGE, ALTERNATING_EXCHANGE), PRESERVING_EXCHANGE)

    def test_one_width_sector_forces_preserving_spatial_pair(self):
        state = pair_state_from_multiplicity("H2", "X", PositiveCount(1))
        self.assertEqual(state.spin_exchange, ALTERNATING_EXCHANGE)
        self.assertEqual(state.spatial_exchange, PRESERVING_EXCHANGE)
        self.assertEqual(state.total_exchange, ALTERNATING_EXCHANGE)
        self.assertEqual(state.same_cell_status, SAME_CELL_ADMITTED)
        self.assertTrue(explicit_occupancy_compatible(state, PositiveCount(2)))

    def test_three_width_sector_forces_alternating_spatial_support(self):
        state = pair_state_from_multiplicity("H2", "a", PositiveCount(3))
        self.assertEqual(state.spin_exchange, PRESERVING_EXCHANGE)
        self.assertEqual(state.spatial_exchange, ALTERNATING_EXCHANGE)
        self.assertEqual(state.same_cell_status, SAME_CELL_EXCLUDED)
        self.assertFalse(explicit_occupancy_compatible(state, PositiveCount(2)))

    def test_invalid_two_electron_multiplicity_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            pair_state_from_multiplicity("H2", "invalid", PositiveCount(2))

    def test_nonalternating_total_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            MolecularElectronPairState(
                HeldLabel("molecular-carrier", "H2"),
                HeldLabel("molecular-electronic-state", "invalid"),
                PositiveCount(1),
                ALTERNATING_EXCHANGE,
                PRESERVING_EXCHANGE,
                PRESERVING_EXCHANGE,
                SAME_CELL_ADMITTED,
            )

    def test_third_identical_occurrence_halts(self):
        state = pair_state_from_multiplicity("H2", "X", PositiveCount(1))
        with self.assertRaises(InadmissibleExactValue):
            explicit_occupancy_compatible(state, PositiveCount(3))

    def test_same_support_partners_remain_distinct(self):
        pair = build_same_support_pair("H2", "3d-pi", "I", "i")
        self.assertNotEqual(pair.singlet_state.state_identity, pair.triplet_state.state_identity)
        self.assertNotEqual(pair.singlet_state.spatial_exchange, pair.triplet_state.spatial_exchange)

    def test_numeric_zero_halts(self):
        with self.assertRaises(FoldLanguageHalt):
            FoldWord((0,))

    def test_capability_closed_prediction_contains_only_universal_law(self):
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(prediction_program_document(ROOT)),
            {"registered-premise": HeldLabel("sealed-derivation", "unit")},
        )
        self.assertIsInstance(execution.output, FoldTable)
        self.assertEqual(len(execution.output.entries), 14)

    def test_complete_nist_h2_exchange_vector(self):
        result = PairExchangeValidator(ROOT).validate(
            SimpleNamespace(seal_hash="sha256:" + "e" * 64)
        )
        self.assertTrue(result.passed)
        self.assertEqual(len(result.measurements), 80)


if __name__ == "__main__":
    unittest.main()
