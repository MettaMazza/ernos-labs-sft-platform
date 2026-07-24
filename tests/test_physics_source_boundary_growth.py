from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

from sft.engine.exact import PositiveCount
from sft.physics.formal_law import FormalPrerequisiteProgram, candidate_rows, survivor_id
from sft.physics.source_boundary_growth import (
    SPEC,
    compatible_positive_exponents,
    monotonic_stop_certificate,
)


ROOT = Path(__file__).resolve().parent.parent


class SourceBoundaryGrowthMethodTests(unittest.TestCase):
    def test_complete_grammar_has_one_survivor(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 1024)
        self.assertEqual(sum(row["candidate_id"] == survivor_id(SPEC) for row in rows), 1)

    def test_method_does_not_preselect_one_exponent(self) -> None:
        self.assertEqual(
            compatible_positive_exponents(Fraction(2, 1), Fraction(3, 1), Fraction(5, 1)),
            (PositiveCount(2),),
        )
        self.assertEqual(
            compatible_positive_exponents(Fraction(3, 1), Fraction(25, 1), Fraction(30, 1)),
            (PositiveCount(3),),
        )

    def test_complete_interval_can_retain_multiple_candidates(self) -> None:
        self.assertEqual(
            compatible_positive_exponents(Fraction(2, 1), Fraction(2, 1), Fraction(4, 1)),
            (PositiveCount(1), PositiveCount(2)),
        )

    def test_invalid_or_unclosed_ratios_halt(self) -> None:
        for values in (
            (Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)),
            (Fraction(2, 1), Fraction(1, 1), Fraction(3, 1)),
            (Fraction(2, 1), Fraction(4, 1), Fraction(3, 1)),
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                compatible_positive_exponents(*values)

    def test_monotonic_stop_is_depth_independent(self) -> None:
        self.assertTrue(monotonic_stop_certificate(Fraction(7, 5), Fraction(100, 1)))

    def test_program_registration_contains_no_free_parameter(self) -> None:
        program = FormalPrerequisiteProgram(SPEC, "sha256:" + "a" * 64)
        self.assertEqual(program.registration.free_parameters, ())
        self.assertEqual(program.registration.axioms, ())

    def test_fixed_exponent_source_is_retained_as_unfavorable_control(self) -> None:
        payload = json.loads(
            (ROOT / "experiments/external_sources/physics/observations_source_boundary_growth.json").read_text(
                encoding="utf-8"
            )
        )
        observation = payload["observations"][0]
        self.assertFalse(observation["protocol_compatible"])
        self.assertFalse(observation["accepted"])
        self.assertEqual(observation["reported_response_values"], "not_tabulated")
        self.assertEqual(observation["reported_model_construction"], "least_squares_with_exponent_fixed_to_two_and_fitted_a_b")
        self.assertFalse(payload["current_result"]["empirical_claim_admitted"])


if __name__ == "__main__":
    unittest.main()
