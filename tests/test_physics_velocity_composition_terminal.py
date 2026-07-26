from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.structural_constants import candidate_rows
from sft.physics.velocity_composition_terminal_law_v1 import (
    EMPTY,
    REST,
    SPEC,
    bilinear_candidates,
    compose_held_pairs,
    compose_same_direction,
    held_pair,
    recover_speed,
    theorem_certificate,
    unique_bilinear_survivor,
)


class VelocityCompositionTerminalTests(unittest.TestCase):
    def test_four_identity_compatible_forms_force_one_survivor(self) -> None:
        self.assertEqual(len(bilinear_candidates()), 4)
        self.assertEqual(sum(bool(row["limit_absorbing"]) for row in bilinear_candidates()), 1)
        self.assertEqual(unique_bilinear_survivor()["candidate_id"], "numerator-cross-absent__denominator-cross-present")

    def test_typed_rest_and_limit(self) -> None:
        for value in (Fraction(1, 8), Fraction(1, 2), Fraction(7, 8), Fraction(1)):
            self.assertEqual(compose_same_direction(REST, value), value)
            self.assertEqual(compose_same_direction(value, REST), value)
            self.assertEqual(compose_same_direction(Fraction(1), value), Fraction(1))
        self.assertIs(held_pair(Fraction(1))[1], EMPTY)

    def test_exact_composition_and_pair_reconstruction(self) -> None:
        self.assertEqual(compose_same_direction(Fraction(1, 2), Fraction(2, 3)), Fraction(7, 8))
        self.assertEqual(compose_same_direction(Fraction(1, 2), Fraction(1, 2)), Fraction(4, 5))
        for left in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)):
            for right in (Fraction(1, 3), Fraction(2, 3), Fraction(1)):
                self.assertEqual(recover_speed(compose_held_pairs(left, right)), compose_same_direction(left, right))

    def test_depth_independent_properties(self) -> None:
        certificate = theorem_certificate()
        self.assertTrue(certificate["closure"])
        self.assertTrue(certificate["strict_sublimit"])
        self.assertTrue(certificate["associativity"])
        self.assertTrue(certificate["pair_equivalence"])
        self.assertTrue(certificate["low_speed_difference_exact"])

    def test_complete_engine_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2048)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2048)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
