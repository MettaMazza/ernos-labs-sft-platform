from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.strong_field_nonlinear_fixed_point_terminal_law_v1 import (
    StrongFieldNonlinearFixedPointProgram,
    candidate_forms,
    field_iteration_certificate,
    finite_strong_fixed_point_test,
    form_survives,
    neutral_source_iteration,
    strong_source_exceeds_positive_bound,
    strong_source_iteration,
)

ROOT = Path(__file__).resolve().parents[1]


class StrongFieldNonlinearFixedPointTests(unittest.TestCase):
    def test_three_iteration_classes_are_exactly_distinct(self):
        certificate = field_iteration_certificate(12)
        self.assertTrue(certificate["neutral_linear_hold"])
        self.assertTrue(certificate["gravity_self_source_contracts"])
        self.assertTrue(certificate["strong_self_source_persists"])
        self.assertEqual(neutral_source_iteration(12)["correction_record"], ())
        self.assertTrue(strong_source_iteration(12)["all_corrections_binary"])

    def test_every_positive_finite_candidate_is_not_fixed(self):
        for candidate in (
            Fraction(1, 4096),
            Fraction(3, 5),
            Fraction(11, 7),
            Fraction(4096, 3),
        ):
            row = finite_strong_fixed_point_test(candidate)
            self.assertTrue(row["successor_strictly_above_candidate"])
            self.assertFalse(row["is_fixed_point"])

    def test_every_positive_exact_bound_has_finite_witness(self):
        for bound in (
            Fraction(1, 127),
            Fraction(3, 5),
            Fraction(11, 7),
            Fraction(4096, 3),
        ):
            witness = strong_source_exceeds_positive_bound(bound)
            self.assertTrue(witness["finite_witness"])
            self.assertTrue(witness["source_exceeds_bound"])

    def test_complete_census(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2916)
        self.assertEqual(len({form.candidate_id for form in forms}), 2916)
        self.assertEqual(len(survivors), 1)

    def test_formal_target_absence(self):
        text = (ROOT / "sft/physics/strong_field_nonlinear_fixed_point_terminal_law_v1.py").read_text()
        for forbidden in (
            "PDG",
            "Particle Data Group",
            "lattice QCD",
            "GeV",
            "string tension",
            "source-record",
            "expected_survivor",
            '"admitted": true',
        ):
            self.assertNotIn(forbidden, text)

    def test_registration_program_and_controls(self):
        program = StrongFieldNonlinearFixedPointProgram("sha256:test")
        census = program.generate_candidates()
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertTrue(program.closure_evidence(decisions).minimality_passed)
        self.assertTrue(all(control.passed for control in program.run_controls()))


if __name__ == "__main__":
    unittest.main()
