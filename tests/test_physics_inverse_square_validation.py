from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

from sft.engine.exact import PositiveCount
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram, candidate_rows, survivor_id
from sft.physics.inverse_square_validation import (
    REPORTED_LOWER,
    REPORTED_SURVIVORS,
    REPORTED_UPPER,
    SOURCE_HASH,
    SOURCE_PATH,
    SPEC,
    positive_integer_exponents_in_interval,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent


class InverseSquareValidationTests(unittest.TestCase):
    def test_complete_grammar_has_one_survivor(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(sum(row["candidate_id"] == survivor_id(SPEC) for row in rows), 1)

    def test_reported_interval_uniquely_retains_two(self) -> None:
        self.assertEqual(REPORTED_SURVIVORS, (PositiveCount(2),))
        self.assertLess(Fraction(1, 1), REPORTED_LOWER)
        self.assertLess(REPORTED_UPPER, Fraction(3, 1))

    def test_checker_retains_every_compatible_positive_integer(self) -> None:
        self.assertEqual(
            positive_integer_exponents_in_interval(Fraction(3, 2), Fraction(7, 2)),
            (PositiveCount(2), PositiveCount(3)),
        )

    def test_invalid_intervals_halt(self) -> None:
        for values in (
            (Fraction(2, 1), Fraction(1, 1)),
            (Fraction(-1, 1), Fraction(2, 1)),
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                positive_integer_exponents_in_interval(*values)

    def test_source_record_hash_and_custody_are_exact(self) -> None:
        self.assertEqual(hash_file(ROOT / SOURCE_PATH), SOURCE_HASH)
        payload = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
        self.assertTrue(payload["custody"]["formal_derivation_was_admitted_before_target_search"])
        self.assertFalse(payload["custody"]["target_identity_was_registered_before_abstract_access"])
        self.assertEqual(payload["reported_observation"]["reported_expression"], "q = (2.7 +/- 3.1) x 10^-16")

    def test_measurement_cannot_supply_formal_exponent(self) -> None:
        self.assertIn("SFT-PHYS-FIELD-INVERSE-SQUARE-001", SPEC.dependencies)
        self.assertNotIn("SFT-PHYS-VALIDATION-INVERSE-SQUARE-001", SPEC.dependencies)
        program = GeneratedEmpiricalPhysicsProgram(SPEC, "sha256:" + "a" * 64)
        self.assertEqual(program.registration.free_parameters, ())
        self.assertEqual(program.registration.axioms, ())

    def test_all_rows_failure_is_preserved(self) -> None:
        ledger = json.loads(
            (ROOT / "experiments/external_sources/physics/observations_inverse_square_validation.json").read_text(
                encoding="utf-8"
            )
        )
        ksu = next(row for row in ledger["observations"] if row["source_id"].startswith("KSU-"))
        self.assertFalse(ksu["accepted_as_validation"])
        self.assertEqual(ksu["complete_consecutive_intersection"], [])
        self.assertEqual(ksu["complete_all_pair_intersection"], [])


if __name__ == "__main__":
    unittest.main()
