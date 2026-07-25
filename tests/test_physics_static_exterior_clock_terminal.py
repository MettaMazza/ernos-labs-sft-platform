from fractions import Fraction
import json
from pathlib import Path
import unittest
from sft.physics.static_exterior_clock_terminal_law_v1 import StaticExteriorClockProgram,candidate_forms,exact_clock_pair,exterior_certificate,exterior_state,form_survives,generated_horizon_radius
from sft.physics.static_exterior_clock_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record
ROOT=Path(__file__).resolve().parents[1]
class StaticExteriorClockTests(unittest.TestCase):
 def test_exact_exterior_flux_and_clock_law(self):
  c=exterior_certificate(12);self.assertEqual(generated_horizon_radius(Fraction(1,4)),Fraction(1,2));self.assertEqual(exterior_state(Fraction(1,4),Fraction(1,2))["clock_record"],());self.assertTrue(c["all_fluxes_equal_horizon"]);self.assertTrue(c["all_well_radius_products_equal_horizon"]);self.assertTrue(c["all_complements_complete_One"]);self.assertTrue(c["well_halves_each_successor"]);self.assertTrue(c["field_quarters_each_successor"]);self.assertTrue(c["coefficient_increases_each_successor"]);self.assertEqual(exact_clock_pair()["far_over_near_rate"],Fraction(16,15))
 def test_complete_census(self):
  forms=candidate_forms();survivors=tuple(form for form in forms if form_survives(form));self.assertEqual(len(forms),2916);self.assertEqual(len({form.candidate_id for form in forms}),2916);self.assertEqual(len(survivors),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/static_exterior_clock_terminal_law_v1.py").read_text()
  for forbidden in ("Schwarzschild","NIST","JILA","Carroll","Birkhoff","1.09e-19","9.8(2.3)","1.28(27)","source-record","expected_survivor",'"admitted": true'):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  analysis=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"]);self.assertTrue(analysis["historical_relation_retained"]);self.assertTrue(analysis["external_unit_conversion_matches"]);self.assertTrue(analysis["nist_direction_matches"]);self.assertTrue(analysis["nist_scope_preserved"]);self.assertTrue(analysis["all_target_rows_retained"]);self.assertFalse(analysis["fitted_value_used"])
 def test_registration_and_program(self):
  registration=json.loads(json.dumps(experiment_registration_record()));self.assertEqual(len(registration["source_hashes"]),10);program=StaticExteriorClockProgram("sha256:test");census=program.generate_candidates();decisions=tuple(program.decide_candidate(candidate) for candidate in census.candidates);self.assertTrue(program.closure_evidence(decisions).minimality_passed);self.assertTrue(all(control.passed for control in program.run_controls()))
if __name__=="__main__":unittest.main()
