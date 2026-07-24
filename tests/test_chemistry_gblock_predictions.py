from pathlib import Path
import unittest

from sft.chemistry.gblock_predictions import (
    GBLOCK_PREDICTION_SPECS,
    fill_configuration,
    generated_subshell_order,
    noble_closures,
    smithium_record,
    subshell_occupation,
)
from sft.chemistry.generated_periodic_law import source_derived_periodic_targets
from sft.physics.atomic_constants import atomic_endpoint, orbit_capacity
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram


ROOT = Path(__file__).resolve().parent.parent


class ChemistryGBlockPredictionTests(unittest.TestCase):
    def test_joint_cover_order_is_complete_and_canonical(self):
        rows = generated_subshell_order(12)
        self.assertEqual(rows[:9], ((1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (3, 3), (4, 2), (5, 1)))
        self.assertEqual(len(rows), len(set(rows)))
        self.assertTrue(all(orbit <= principal for principal, orbit in rows))

    def test_known_closures_and_g_block_opening(self):
        self.assertEqual(noble_closures(7), (2, 10, 18, 36, 54, 86, 118))
        self.assertEqual(subshell_occupation(118, 5, 5), ())
        self.assertEqual(subshell_occupation(119, 8, 1), (1,))
        self.assertEqual(subshell_occupation(120, 8, 1), (2,))
        self.assertEqual(subshell_occupation(120, 5, 5), ())
        self.assertEqual(subshell_occupation(121, 5, 5), (1,))
        self.assertEqual(orbit_capacity(5), 18)

    def test_smithium_record_is_exact(self):
        self.assertEqual(
            smithium_record(),
            {
                "proton": 126,
                "neutron": 184,
                "mass": 310,
                "configuration": ((8, 1, 2), (5, 5, 6)),
                "valence": 8,
                "predicted_positive_oxidation_counts": (2, 3, 4, 5, 6, 7, 8),
            },
        )

    def test_all_neutral_configurations_close_through_endpoint(self):
        for atomic_number in range(1, atomic_endpoint() + 1):
            rows = fill_configuration(atomic_number)
            self.assertEqual(sum(row.occupied for row in rows), atomic_number)
            self.assertTrue(all(row.occupied <= row.capacity for row in rows))

    def test_specs_have_one_survivor_and_source_labels_reconstruct(self):
        for spec in GBLOCK_PREDICTION_SPECS:
            with self.subTest(spec.claim_id):
                program = GeneratedEmpiricalPhysicsProgram(spec, "sha256:" + "1" * 64)
                census = program.generate_candidates()
                decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
                self.assertEqual(len(census.candidates), 256)
                self.assertEqual(sum(row.survives for row in decisions), 1)
                targets, _ = source_derived_periodic_targets(ROOT, spec)
                self.assertEqual(len(targets), 1)
                self.assertEqual(targets[0]["observed_label"], spec.expected_observation_label)


if __name__ == "__main__":
    unittest.main()
