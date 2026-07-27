from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.orbital_support_law_v1 import (
    OccupiedMolecularSupport,
    axis_rank_from_positive_ordinal,
    conventional_support_correspondence,
    joined_phase_pair,
    occupied_support_from_source_assignment,
)
from sft.chemistry.orbital_support_validation_v1 import OrbitalSupportValidator, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldTable, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class OrbitalSupportTests(unittest.TestCase):
    def test_axis_boundary_is_empty_one(self):
        self.assertEqual(axis_rank_from_positive_ordinal(PositiveCount(1)), EMPTY_ONE)

    def test_axis_successors_are_positive(self):
        self.assertEqual(axis_rank_from_positive_ordinal(PositiveCount(4)), PositiveCount(3))

    def test_joining_forces_two_phases(self):
        phases = joined_phase_pair("molecule", PositiveCount(1), EMPTY_ONE)
        self.assertEqual(len(phases), 2)
        self.assertNotEqual(phases[0], phases[1])

    def test_single_occupancy(self):
        row = occupied_support_from_source_assignment("H2+", PositiveCount(1), "σ", PositiveCount(1))
        self.assertEqual(row.occupancy_count, PositiveCount(1))

    def test_complementary_pair_occupancy(self):
        row = occupied_support_from_source_assignment("H2", PositiveCount(1), "σ", PositiveCount(2))
        self.assertEqual({x.label for x in row.spin_fibres}, {"fibre-a", "fibre-b"})

    def test_triple_occupancy_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            occupied_support_from_source_assignment("bad", PositiveCount(1), "σ", PositiveCount(3))

    def test_same_spin_pair_halts(self):
        cell = joined_phase_pair("bad", PositiveCount(1), EMPTY_ONE)[0]
        with self.assertRaises(InadmissibleExactValue):
            OccupiedMolecularSupport(cell, (HeldLabel("electron-occurrence", "a"), HeldLabel("electron-occurrence", "b")), (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-a")))

    def test_conventional_correspondence_is_exact(self):
        self.assertEqual(conventional_support_correspondence("Σ"), EMPTY_ONE)
        self.assertEqual(conventional_support_correspondence("Φ"), PositiveCount(3))

    def test_unknown_correspondence_halts(self):
        with self.assertRaises(InadmissibleExactValue):
            conventional_support_correspondence("unknown")

    def test_prediction_is_capability_closed_table(self):
        program = fold_program_from_mapping(prediction_program_document(ROOT))
        result = CapabilityClosedFoldInterpreter().execute(program, {"registered-premise": HeldLabel("sealed-derivation", "unit")})
        self.assertIsInstance(result.output, FoldTable)
        self.assertEqual(len(result.output.entries), 32)

    def test_complete_NIST_vector_passes(self):
        result = OrbitalSupportValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "c" * 64))
        self.assertTrue(result.passed)
        self.assertEqual(len(result.measurements), 366)


if __name__ == "__main__":
    unittest.main()
