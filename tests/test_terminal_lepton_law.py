from fractions import Fraction
from pathlib import Path
import unittest

from sft.engine import ProvenanceClass
from sft.physics.charged_lepton_validation import comparison_record
from sft.physics.structural_constants import candidate_rows
from sft.physics.terminal_lepton_law import (
    TERMINAL_LEPTON_SPEC,
    terminal_product_invariant,
    terminal_self_coupling_correction,
)


ROOT = Path(__file__).resolve().parents[1]


class TerminalLeptonLawTests(unittest.TestCase):
    def test_complete_structural_grammar_has_one_declared_survivor(self) -> None:
        rows = candidate_rows(TERMINAL_LEPTON_SPEC)
        self.assertEqual(len(rows), 1024)
        self.assertEqual(
            TERMINAL_LEPTON_SPEC.provenance,
            (ProvenanceClass.OBSERVATIONAL_DERIVATION,),
        )

    def test_terminal_result_is_exact_positive_and_parameter_free(self) -> None:
        correction = terminal_self_coupling_correction()
        result = terminal_product_invariant()
        self.assertIsInstance(result, Fraction)
        self.assertGreater(correction, 0)
        self.assertGreater(result, 0)
        self.assertEqual(result + correction, Fraction(3, 1454))

    def test_terminal_prediction_passes_every_registered_codata_row(self) -> None:
        record = comparison_record(ROOT, terminal_product_invariant())
        self.assertTrue(record["all_rows_passed"])
        self.assertTrue(record["muon_electron"]["overlap"])
        self.assertTrue(record["muon_tau"]["overlap"])


if __name__ == "__main__":
    unittest.main()
