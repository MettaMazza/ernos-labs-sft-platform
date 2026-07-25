from fractions import Fraction
import json
from pathlib import Path
import unittest
from sft.physics.coupled_map_criticality_terminal_law_v1 import CoupledMapCriticalityProgram,candidate_forms,criticality_certificate,form_survives,holding_threshold,retained_transverse_multiplier,stability_class
from sft.physics.coupled_map_criticality_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record
ROOT=Path(__file__).resolve().parents[1]
class CoupledMapCriticalityTests(unittest.TestCase):
 def test_general_threshold(self):
  for m in (2,3,5,7):
   t=holding_threshold(m);self.assertEqual(retained_transverse_multiplier(m,t),1);self.assertEqual(stability_class(m,Fraction(m-1,m+1)),"strict-expansion");self.assertEqual(stability_class(m,Fraction(m,m+1)),"strict-contraction")
  self.assertTrue(criticality_certificate()["binary_threshold_is_half_One"])
 def test_complete_census(self):
  forms=candidate_forms();survivors=tuple(f for f in forms if form_survives(f));self.assertEqual(len(forms),2916);self.assertEqual(len({f.candidate_id for f in forms}),2916);self.assertEqual(len(survivors),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/coupled_map_criticality_terminal_law_v1.py").read_text()
  for forbidden in ("nlin/0504012","15447575","0.867","source-record","expected_survivor",'"admitted": true',"PhysRevE"):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  a=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"]);self.assertEqual(a["forced_threshold"],Fraction(1,2));self.assertEqual(a["classes"],("strict-expansion","neutral-boundary","strict-contraction"));self.assertTrue(a["topology_dependent_bounds_retained"]);self.assertEqual(a["complete_target_row_count"],20)
 def test_registration_and_program(self):
  reg=json.loads(json.dumps(experiment_registration_record()));self.assertEqual(len(reg["source_hashes"]),3);p=CoupledMapCriticalityProgram("sha256:test");c=p.generate_candidates();d=tuple(p.decide_candidate(x) for x in c.candidates);self.assertTrue(p.closure_evidence(d).minimality_passed);self.assertTrue(all(x.passed for x in p.run_controls()))
if __name__=="__main__":unittest.main()
