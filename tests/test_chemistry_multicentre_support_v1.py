from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.multicentre_support_law_v1 import DelocalizedMolecularSupport, RIBBON, SURFACE, VOLUME, ribbon_support, surface_cycle_support, tetrahedral_volume_support
from sft.chemistry.multicentre_support_validation_v1 import MulticentreSupportValidator, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, FoldWord, fold_program_from_mapping
from sft.claim_evidence.fold_language import FoldLanguageHalt
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class MulticentreSupportTests(unittest.TestCase):
    def test_three_centre_bridge(self):
        support = ribbon_support("diborane", ("B-left", "H-bridge", "B-right"))
        self.assertEqual(support.topology, RIBBON)
        self.assertEqual(support.positive_centre_count, PositiveCount(3))
        self.assertTrue(support.irreducible_to_one_localized_pair)

    def test_six_centre_surface_cycle(self):
        support = surface_cycle_support("benzene", tuple(f"C-{position}" for position in range(1, 7)))
        self.assertEqual(support.topology, SURFACE)
        self.assertEqual(support.positive_edge_count, PositiveCount(6))

    def test_four_centre_volume(self):
        support = tetrahedral_volume_support("tetrahedrane", ("one", "two", "three", "four"))
        self.assertEqual(support.topology, VOLUME)
        self.assertEqual(support.positive_edge_count, PositiveCount(6))

    def test_two_centres_halt(self):
        with self.assertRaises(InadmissibleExactValue):
            ribbon_support("invalid", ("left", "right"))

    def test_disconnected_support_halts(self):
        support = ribbon_support("control", ("one", "two", "three"))
        with self.assertRaises(InadmissibleExactValue):
            DelocalizedMolecularSupport(support.molecular_carrier, RIBBON, support.centres, support.edges[:1], support.electron_support)

    def test_incomplete_support_word_halts(self):
        support = ribbon_support("control", ("one", "two", "three"))
        with self.assertRaises(InadmissibleExactValue):
            DelocalizedMolecularSupport(support.molecular_carrier, RIBBON, support.centres, support.edges, FoldWord(support.centres[:-1]))

    def test_wrong_topology_halts(self):
        support = surface_cycle_support("control", ("one", "two", "three"))
        with self.assertRaises(InadmissibleExactValue):
            DelocalizedMolecularSupport(support.molecular_carrier, RIBBON, support.centres, support.edges, support.electron_support)

    def test_numeric_zero_halts(self):
        with self.assertRaises(FoldLanguageHalt):
            FoldWord((0,))

    def test_capability_closed_prediction_contains_only_universal_law(self):
        execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(prediction_program_document(ROOT)), {"registered-premise": HeldLabel("sealed-derivation", "unit")})
        self.assertIsInstance(execution.output, FoldTable)
        self.assertEqual(len(execution.output.entries), 8)

    def test_complete_external_vector(self):
        result = MulticentreSupportValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "e" * 64))
        self.assertTrue(result.passed)
        self.assertEqual(len(result.measurements), 41)


if __name__ == "__main__":
    unittest.main()
