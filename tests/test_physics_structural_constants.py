from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.structural_constants import (
    BOUNDARY_RANK_SPEC,
    GENERATOR_THREE_SPEC,
    INVERSE_SQUARE_SPEC,
    SPATIAL_THREE_SPEC,
    StructuralPhysicsProgram,
    boundary_growth,
    boundary_rank_two,
    candidate_rows,
    first_return_trace,
    fold_part,
    generator_period_three,
    generator_unit_part,
    inverse_square_response,
    spatial_dimension_three,
    stable_spatial_counts,
    survivor_id,
)


class StructuralPhysicsTests(unittest.TestCase):
    def test_exact_fold_orbits_force_periods_two_and_three(self) -> None:
        self.assertEqual(generator_unit_part(2), Fraction(1, 3))
        self.assertEqual(generator_unit_part(3), Fraction(1, 7))
        self.assertEqual(first_return_trace(Fraction(1, 3)), (Fraction(2, 3), Fraction(1, 3)))
        self.assertEqual(
            first_return_trace(Fraction(1, 7)),
            (Fraction(2, 7), Fraction(4, 7), Fraction(1, 7)),
        )
        self.assertEqual(generator_period_three(), 3)

    def test_fold_domain_and_nonreturning_part_halt(self) -> None:
        for value in (Fraction(-1, 2), Fraction(0, 1), Fraction(3, 2)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fold_part(value)
        with self.assertRaises(ValueError):
            first_return_trace(Fraction(1, 2))

    def test_spatial_stability_is_complete_and_cross_locked(self) -> None:
        self.assertEqual(stable_spatial_counts(2), (3,))
        self.assertEqual(spatial_dimension_three(), 3)
        with self.assertRaises(ValueError):
            stable_spatial_counts(1)

    def test_boundary_rank_and_growth_are_exact(self) -> None:
        self.assertEqual(boundary_rank_two(), 2)
        self.assertEqual(boundary_growth(Fraction(2, 1)), Fraction(4, 1))
        self.assertEqual(boundary_growth(Fraction(3, 2)), Fraction(9, 4))
        with self.assertRaises(ValueError):
            boundary_growth(Fraction(1, 1))

    def test_inverse_square_response_conserves_source(self) -> None:
        source = Fraction(7, 11)
        ratio = Fraction(5, 3)
        response = inverse_square_response(source, ratio)
        self.assertEqual(response, Fraction(63, 275))
        self.assertEqual(response * boundary_growth(ratio), source)

    def test_every_registered_grammar_has_one_survivor(self) -> None:
        expected = {
            GENERATOR_THREE_SPEC.claim_id: 1024,
            SPATIAL_THREE_SPEC.claim_id: 1024,
            BOUNDARY_RANK_SPEC.claim_id: 2048,
            INVERSE_SQUARE_SPEC.claim_id: 4096,
        }
        for spec in (GENERATOR_THREE_SPEC, SPATIAL_THREE_SPEC, BOUNDARY_RANK_SPEC, INVERSE_SQUARE_SPEC):
            with self.subTest(claim_id=spec.claim_id):
                rows = candidate_rows(spec)
                self.assertEqual(len(rows), expected[spec.claim_id])
                self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)

    def test_registrations_have_no_axioms_or_parameters(self) -> None:
        for spec in (GENERATOR_THREE_SPEC, SPATIAL_THREE_SPEC, BOUNDARY_RANK_SPEC, INVERSE_SQUARE_SPEC):
            registration = StructuralPhysicsProgram(spec, "sha256:" + "a" * 64).registration
            self.assertEqual(registration.axioms, ())
            self.assertEqual(registration.free_parameters, ())
            self.assertEqual(registration.dependencies, spec.dependencies)


if __name__ == "__main__":
    unittest.main()
