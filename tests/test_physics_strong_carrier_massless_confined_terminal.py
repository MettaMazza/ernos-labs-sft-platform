from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.strong_carrier_massless_confined_terminal_law_v1 import (
    StrongCarrierMasslessConfinedProgram,
    candidate_forms,
    confining_tube_trace,
    form_survives,
    massless_causal_trace,
    simultaneous_carrier_certificate,
    strong_sector_structure,
    work_exceeds_positive_bound,
)
from sft.physics.strong_carrier_massless_confined_terminal_validation_v1 import (
    authoritative_record,
    exact_measurement_analysis,
    experiment_registration_record,
)

ROOT = Path(__file__).resolve().parents[1]


class StrongCarrierMasslessConfinedTests(unittest.TestCase):
    def test_simultaneous_massless_One_speed_and_confined(self):
        structure = strong_sector_structure()
        certificate = simultaneous_carrier_certificate(32)
        self.assertEqual(structure["mediator_count"], 8)
        self.assertEqual(structure["coupling"], Fraction(2, 3))
        self.assertEqual(structure["mass_label"], ())
        self.assertTrue(certificate["simultaneously_massless_and_One_speed"])
        self.assertTrue(certificate["simultaneously_confined"])
        self.assertTrue(certificate["confinement_does_not_create_mass_label"])

    def test_depth_independent_causal_and_tube_successors(self):
        causal = massless_causal_trace(64)
        tube = confining_tube_trace(64)
        self.assertTrue(causal["all_increments_One"])
        self.assertTrue(causal["phase_retained"])
        self.assertEqual(causal["rest_capture_record"], ())
        self.assertTrue(tube["width_fixed"])
        self.assertTrue(tube["field_fixed"])
        self.assertTrue(tube["all_work_increments_equal_coupling"])
        self.assertEqual(tube["isolated_colour_carrier_record"], ())

    def test_every_positive_exact_bound_has_finite_witness(self):
        for bound in (
            Fraction(1, 127),
            Fraction(3, 5),
            Fraction(11, 7),
            Fraction(4096, 3),
        ):
            witness = work_exceeds_positive_bound(bound)
            self.assertTrue(witness["finite_witness"])
            self.assertTrue(witness["exceeds_bound"])

    def test_complete_census(self):
        forms = candidate_forms()
        survivors = tuple(form for form in forms if form_survives(form))
        self.assertEqual(len(forms), 2916)
        self.assertEqual(len({form.candidate_id for form in forms}), 2916)
        self.assertEqual(len(survivors), 1)

    def test_formal_target_absence(self):
        text = (ROOT / "sft/physics/strong_carrier_massless_confined_terminal_law_v1.py").read_text()
        for forbidden in (
            "PDG",
            "Particle Data Group",
            "lattice QCD",
            "GeV",
            "experimental mass limit",
            "source-record",
            "expected_survivor",
            '"admitted": true',
        ):
            self.assertNotIn(forbidden, text)

    def test_registration_program_and_controls(self):
        program = StrongCarrierMasslessConfinedProgram("sha256:test")
        census = program.generate_candidates()
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertTrue(program.closure_evidence(decisions).minimality_passed)
        self.assertTrue(all(control.passed for control in program.run_controls()))

    def test_postseal_complete_pdg_comparison(self):
        record = authoritative_record(ROOT)
        analysis = exact_measurement_analysis(record["registered_target"])
        self.assertTrue(analysis["all_target_rows_retained"])
        self.assertTrue(analysis["historical_joint_relation_retained"])
        self.assertTrue(analysis["pdg_three_eight_correspondence"])
        self.assertTrue(analysis["pdg_massless_classification_correspondence"])
        self.assertTrue(analysis["pdg_mass_value_is_theoretical_not_direct_measurement"])
        self.assertTrue(analysis["pdg_mass_caveat_retained"])
        self.assertTrue(analysis["pdg_self_source_correspondence"])
        self.assertTrue(analysis["pdg_confinement_correspondence"])
        self.assertTrue(analysis["measured_CA_contains_expected"])
        self.assertTrue(analysis["measured_CF_contains_expected"])
        self.assertFalse(analysis["direct_free_gluon_time_of_flight_available"])
        self.assertFalse(analysis["external_values_select_formal_survivor"])
        self.assertFalse(analysis["external_mass_value_used_as_formal_proof"])
        self.assertFalse(analysis["fitted_value_used"])
        self.assertFalse(analysis["free_correction_used"])
        self.assertEqual(len(experiment_registration_record()["source_hashes"]), 15)


if __name__ == "__main__":
    unittest.main()
