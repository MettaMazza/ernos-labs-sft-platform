from fractions import Fraction
import json
from pathlib import Path
import unittest
from sft.physics.post_newtonian_fixed_point_terminal_law_v1 import PostNewtonianFixedPointProgram,admissible_fixed_points,candidate_forms,convergence_certificate,fixed_point_candidates,form_survives,iterate,structural_values
from sft.physics.post_newtonian_fixed_point_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record
ROOT=Path(__file__).resolve().parents[1]
class PostNewtonianFixedPointTests(unittest.TestCase):
 def test_exact_fixed_point_and_depth_independent_contraction(self):
  self.assertEqual(structural_values(),{"matter":Fraction(7,16),"coupling":Fraction(1,2),"fixed":Fraction(1,4)});self.assertEqual(fixed_point_candidates(),(Fraction(1,4),Fraction(7,4)));self.assertEqual(admissible_fixed_points(),(Fraction(1,4),));c=convergence_certificate(12);self.assertTrue(c["values_increase_below_fixed"]);self.assertTrue(c["errors_strictly_shrink"]);self.assertTrue(c["corrections_strictly_shrink"]);self.assertTrue(c["all_factors_below_quarter"])
 def test_complete_census(self):
  forms=candidate_forms();survivors=tuple(form for form in forms if form_survives(form));self.assertEqual(len(forms),2916);self.assertEqual(len({form.candidate_id for form in forms}),2916);self.assertEqual(len(survivors),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/post_newtonian_fixed_point_terminal_law_v1.py").read_text()
  for forbidden in ("arxiv","Blanchet","source-record","expected_survivor",'"admitted": true',"7/50","7/150","7/1350","7/109350"):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  analysis=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"]);self.assertEqual(analysis["structural_values"],{"matter":Fraction(7,16),"coupling":Fraction(1,2),"fixed":Fraction(1,4)});self.assertTrue(analysis["all_target_rows_retained"]);self.assertTrue(analysis["v1_corrections_strictly_shrink"]);self.assertTrue(analysis["v2_map_rows_match"]);self.assertTrue(analysis["external_universal_numeric_convergence_not_claimed"]);self.assertFalse(analysis["fitted_value_used"])
 def test_registration_and_program(self):
  registration=json.loads(json.dumps(experiment_registration_record()));self.assertEqual(len(registration["source_hashes"]),4);program=PostNewtonianFixedPointProgram("sha256:test");census=program.generate_candidates();decisions=tuple(program.decide_candidate(candidate) for candidate in census.candidates);self.assertTrue(program.closure_evidence(decisions).minimality_passed);self.assertTrue(all(control.passed for control in program.run_controls()));self.assertEqual(iterate(1)[0],Fraction(7,32))
if __name__=="__main__":unittest.main()
