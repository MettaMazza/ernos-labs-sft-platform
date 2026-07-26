import unittest
from fractions import Fraction

from sft.physics.gravitational_wave_chirp_ringdown_terminal_law_v1 import (
    CONTACT_SEPARATION,
    SPEC,
    inspiral_certificate,
    merger_record,
    ringdown_certificate,
    theorem_certificate,
)
from sft.physics.structural_constants import candidate_rows


class GravitationalWaveChirpRingdownTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)

    def test_depth_independent_chirp(self):
        for depth in (1, 2, 3, 8, 16, 32):
            row = inspiral_certificate(depth)
            self.assertTrue(row["separation_strictly_falls"])
            self.assertTrue(row["period_squared_strictly_falls"])
            self.assertTrue(row["orbital_frequency_squared_strictly_rises"])
            self.assertTrue(row["wave_frequency_squared_strictly_rises"])
            self.assertTrue(row["quadrupole_is_twice_orbital"])
            self.assertTrue(row["every_successor_take_positive"])
            self.assertTrue(row["ends_at_horizon_contact"])

    def test_contact_merger_retains_ledger(self):
        row = merger_record()
        self.assertEqual(row["contact_separation"], CONTACT_SEPARATION)
        self.assertEqual(row["initial_source_count"], 2)
        self.assertEqual(row["joined_source_count"], 1)
        self.assertTrue(row["radiation_record"])
        self.assertEqual(row["component_radius"], Fraction(1, 2))

    def test_ringdown_and_complete_sequence(self):
        for depth in (1, 2, 3, 8, 16, 32):
            row = ringdown_certificate(depth)
            self.assertTrue(row["one_remnant"])
            self.assertTrue(row["tone_held"])
            self.assertTrue(row["binary_damping"])
            self.assertTrue(row["all_reached_amplitudes_positive"])
            self.assertTrue(row["finite_floor_retained"])
        theorem = theorem_certificate()
        self.assertTrue(theorem["all_chirps_close"])
        self.assertTrue(theorem["merger_closes"])
        self.assertTrue(theorem["all_ringdowns_close"])
        self.assertEqual(theorem["unique_ordered_sequence"], ("inspiral-rising-chirp", "merger", "damped-ringdown"))


if __name__ == "__main__":
    unittest.main()
