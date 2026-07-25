from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.quadrupole_radiated_power_terminal_law_v1 import (
    QuadrupoleRadiatedPowerProgram,
    candidate_forms,
    cubic_opposition_identity,
    form_survives,
    generated_difference_record,
    generated_quadrupole_trace,
    quadrupole_power_record,
    radiated_power_certificate,
    static_quadrupole_trace,
)
from sft.physics.quadrupole_radiated_power_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
    experiment_registration_record,
)

ROOT = Path(__file__).resolve().parents[1]


class QuadrupoleRadiatedPowerTests(unittest.TestCase):
    def test_exact_third_difference_power_and_static_control(self):
        certificate = radiated_power_certificate(16)
        self.assertEqual(set(certificate["base_third_record"]), {Fraction(6, 1)})
        self.assertEqual(certificate["base_power"], Fraction(18, 1))
        self.assertEqual(certificate["doubled_power"], Fraction(72, 1))
        self.assertEqual(quadrupole_power_record(static_quadrupole_trace()), ())
        self.assertTrue(certificate["third_rate_doubles"])
        self.assertTrue(certificate["power_quadruples"])
        self.assertTrue(certificate["shell_power_conserved"])

    def test_depth_independent_positive_identity(self):
        for index in range(1, 65):
            row = cubic_opposition_identity(index)
            self.assertTrue(row["identity_holds"])
            self.assertTrue(row["successor_preserves_identity"])
        trace = generated_quadrupole_trace(Fraction(5, 7), 20)
        self.assertEqual(set(generated_difference_record(trace, 3)), {Fraction(30, 7)})

    def test_complete_census(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2916)
        self.assertEqual(len({form.candidate_id for form in forms}), 2916)
        self.assertEqual(len(survivors), 1)

    def test_formal_target_absence(self):
        text = (ROOT / "sft/physics/quadrupole_radiated_power_terminal_law_v1.py").read_text()
        for forbidden in (
            "Hulse",
            "Taylor",
            "Weisberg",
            "Kramer",
            "B1913",
            "J0737",
            "32/5",
            "measured orbital decay",
            "source-record",
            "expected_survivor",
            '"admitted": true',
        ):
            self.assertNotIn(forbidden, text)

    def test_registration_program_and_controls(self):
        program = QuadrupoleRadiatedPowerProgram("sha256:test")
        census = program.generate_candidates()
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertTrue(program.closure_evidence(decisions).minimality_passed)
        self.assertTrue(all(control.passed for control in program.run_controls()))

    def test_postseal_complete_binary_comparison(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(record["registered_target"])
        self.assertTrue(analysis["all_target_rows_retained"])
        self.assertTrue(analysis["historical_relation_retained"])
        self.assertTrue(analysis["primary_quadrupole_classification_matches"])
        self.assertTrue(analysis["measured_contains_One_at_published_uncertainty"])
        self.assertTrue(analysis["measured_within_95_percent_boundary"])
        self.assertTrue(analysis["extreme_EOS_contains_One"])
        self.assertFalse(analysis["negative_external_sign_used_as_proof"])
        self.assertFalse(analysis["fitted_value_used"])
        self.assertFalse(analysis["free_correction_used"])
        self.assertEqual(len(experiment_registration_record()["source_hashes"]), 11)


if __name__ == "__main__":
    unittest.main()
