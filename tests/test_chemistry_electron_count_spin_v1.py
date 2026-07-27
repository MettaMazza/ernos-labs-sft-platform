from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.electron_count_spin_law_v1 import (
    HeldChargeTransfer,
    NuclearPopulation,
    SpinCell,
    build_complete_spin_organization,
    exact_electron_count,
    required_spin_width_parity,
)
from sft.chemistry.electron_count_spin_validation_v1 import (
    ElectronCountSpinValidator,
    prediction_program_document,
    prediction_rows,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def population(symbol: str, atomic_number: int, occurrences: int) -> NuclearPopulation:
    return NuclearPopulation(
        HeldLabel("element-symbol", symbol),
        PositiveCount(atomic_number),
        PositiveCount(occurrences),
    )


class ElectronCountSpinLawTests(unittest.TestCase):
    def test_neutral_count_uses_structural_empty_one(self) -> None:
        count = exact_electron_count(
            (population("C", 6, 1), population("O", 8, 1)),
            HeldChargeTransfer(HeldLabel("electron-transfer", "empty-One"), EMPTY_ONE),
        )
        self.assertEqual(count, PositiveCount(14))

    def test_cation_removes_one_positive_occurrence(self) -> None:
        count = exact_electron_count(
            (population("O", 8, 2),),
            HeldChargeTransfer(HeldLabel("electron-transfer", "remove-electron"), PositiveCount(1)),
        )
        self.assertEqual(count, PositiveCount(15))

    def test_anion_adjoins_one_positive_occurrence(self) -> None:
        count = exact_electron_count(
            (population("O", 8, 2),),
            HeldChargeTransfer(HeldLabel("electron-transfer", "adjoin-electron"), PositiveCount(1)),
        )
        self.assertEqual(count, PositiveCount(17))

    def test_removal_cannot_erase_positive_support(self) -> None:
        with self.assertRaises(InadmissibleExactValue):
            exact_electron_count(
                (population("H", 1, 1),),
                HeldChargeTransfer(HeldLabel("electron-transfer", "remove-electron"), PositiveCount(1)),
            )

    def test_even_count_forces_odd_width_parity(self) -> None:
        self.assertEqual(required_spin_width_parity(PositiveCount(16)).label, "odd-positive-width")

    def test_odd_count_forces_even_width_parity(self) -> None:
        self.assertEqual(required_spin_width_parity(PositiveCount(15)).label, "even-positive-width")

    def test_triplet_oxygen_reconstructs_pairs_and_unmatched_fibres(self) -> None:
        organization = build_complete_spin_organization("oxygen", PositiveCount(16), PositiveCount(3))
        self.assertEqual(organization.complementary_pair_count, PositiveCount(7))
        self.assertEqual(organization.unmatched_fibre_count, PositiveCount(2))
        self.assertEqual(sum(len(cell.occupants) for cell in organization.cells), 16)

    def test_wrong_width_parity_halts(self) -> None:
        with self.assertRaises(InadmissibleExactValue):
            build_complete_spin_organization("tampered", PositiveCount(14), PositiveCount(2))

    def test_same_fibre_same_cell_halts(self) -> None:
        with self.assertRaises(InadmissibleExactValue):
            SpinCell(
                HeldLabel("electron-support-cell", "tampered"),
                (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-a")),
            )

    def test_prediction_vector_is_complete_and_capability_closed(self) -> None:
        rows = prediction_rows(ROOT)
        self.assertEqual(len(rows), 22)
        self.assertEqual(rows[0]["electron_count"], 2)
        self.assertEqual(rows[-1]["electron_count"], 16)
        program = fold_program_from_mapping(prediction_program_document(ROOT))
        execution = CapabilityClosedFoldInterpreter().execute(
            program,
            {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
        )
        self.assertIsInstance(execution.output, FoldTable)
        self.assertEqual(len(execution.output.entries), 22)

    def test_complete_post_seal_source_vector_and_adverse_controls_pass(self) -> None:
        sealed = SimpleNamespace(seal_hash="sha256:" + "a" * 64)
        result = ElectronCountSpinValidator(ROOT).validate(sealed)
        self.assertTrue(result.passed)
        self.assertTrue(result.all_rows_preserved)
        self.assertEqual(len(result.measurements), 27)


if __name__ == "__main__":
    unittest.main()
