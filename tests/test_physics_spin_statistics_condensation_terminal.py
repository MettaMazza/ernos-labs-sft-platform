from fractions import Fraction
import unittest

from sft.physics.spin_statistics_condensation_terminal_law_v1 import (
    SPEC,
    canonical_mean_throw,
    canonical_occupation_weights,
    critical_condensation_certificate,
    exchange_spin_census,
    ground_share,
    minimal_throw_ground_certificate,
    occupation_census,
    occupation_vectors,
    spin_return_certificate,
    theorem_certificate,
)
from sft.physics.structural_constants import candidate_rows


class Tests(unittest.TestCase):
    def test_complete_occupation_census(self):
        row = occupation_census(3, 4)
        self.assertTrue(row["complete"])
        self.assertEqual(row["boson_count"], 20)
        self.assertEqual(row["fermion_count"], 4)
        self.assertIn((3, 0, 0, 0), row["boson_vectors"])
        self.assertNotIn((2, 1, 0, 0), row["fermion_vectors"])
        self.assertEqual(occupation_vectors(5, 3, "alternating"), ())

    def test_exact_finite_weights(self):
        for exchange in ("preserving", "alternating"):
            rows = canonical_occupation_weights(2, 4, exchange, 3)
            self.assertEqual(sum((weight for _, weight in rows), Fraction(0)), 1)
            self.assertTrue(all(isinstance(weight, Fraction) and weight > 0 for _, weight in rows))
        self.assertGreater(ground_share(4, 3, "preserving", 3), ground_share(4, 3, "preserving", 2))
        self.assertLess(canonical_mean_throw(4, 3, "preserving", 3), canonical_mean_throw(4, 3, "preserving", 2))

    def test_spin_and_pairing(self):
        spin = exchange_spin_census()
        self.assertEqual(spin["preserving_share"], Fraction(3, 4))
        self.assertEqual(spin["alternating_share"], Fraction(1, 4))
        returns = spin_return_certificate()
        self.assertEqual(returns["alternating_first_return_turns"], 2)
        self.assertEqual(returns["paired_first_return_turns"], 1)
        self.assertEqual(returns["two_alternating_compose_to"], "preserving")

    def test_condensation(self):
        for factor in range(2, 6):
            for levels in range(2, 6):
                for particles in range(2, 8):
                    row = critical_condensation_certificate(particles, levels, factor)
                    self.assertGreaterEqual(row["ground_share"], row["lock_share"])
                    self.assertTrue(row["prior_below"])
                    self.assertTrue(minimal_throw_ground_certificate(particles, levels)["unique"])
        binary = critical_condensation_certificate(10, 4, 2)
        self.assertEqual(binary["lock_share"], Fraction(1, 2))
        self.assertEqual(binary["critical_depth"], 2)

    def test_invalid_boundaries(self):
        with self.assertRaises(ValueError):
            occupation_vectors(0, 2, "preserving")
        with self.assertRaises(ValueError):
            occupation_vectors(2, 0, "preserving")
        with self.assertRaises(ValueError):
            occupation_vectors(2, 2, "unknown")
        with self.assertRaises(ValueError):
            canonical_occupation_weights(2, 2, "preserving", 0)
        with self.assertRaises(ValueError):
            critical_condensation_certificate(2, 1, 2)
        with self.assertRaises(ValueError):
            critical_condensation_certificate(2, 2, 1)

    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertTrue(all(theorem_certificate().values()))
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
