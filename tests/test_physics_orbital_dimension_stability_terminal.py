from fractions import Fraction
import json
from pathlib import Path
import unittest
from sft.physics.orbital_dimension_stability_terminal_law_v1 import OrbitalDimensionStabilityProgram,candidate_forms,dimension_certificate,form_survives,orbital_stability_class
from sft.physics.orbital_dimension_stability_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record
ROOT=Path(__file__).resolve().parents[1]
class OrbitalDimensionStabilityTests(unittest.TestCase):
 def test_all_dimension_partition(self):
  for d in range(2,13):
   expected="stable-restoring" if d<4 else "marginal" if d==4 else "unstable-nonrestoring"
   for q in (Fraction(3,2),Fraction(2,1),Fraction(5,2)):self.assertEqual(orbital_stability_class(d,q),expected)
  self.assertFalse(dimension_certificate()["negative_exponent_required"])
 def test_complete_census(self):
  forms=candidate_forms();s=tuple(f for f in forms if form_survives(f));self.assertEqual(len(forms),2916);self.assertEqual(len({f.candidate_id for f in forms}),2916);self.assertEqual(len(s),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/orbital_dimension_stability_terminal_law_v1.py").read_text();
  for forbidden in ("cambridge","Tong","source-record","expected_survivor",'"admitted": true',"Ehrenfest"):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  a=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"]);self.assertEqual(a["stable_dimensions"],(2,3));self.assertEqual(a["marginal_dimensions"],(4,));self.assertEqual(a["unstable_dimensions"],tuple(range(5,13)));self.assertTrue(a["all_target_rows_retained"])
 def test_registration_and_program(self):
  reg=json.loads(json.dumps(experiment_registration_record()));self.assertEqual(len(reg["source_hashes"]),3);p=OrbitalDimensionStabilityProgram("sha256:test");c=p.generate_candidates();d=tuple(p.decide_candidate(x) for x in c.candidates);self.assertTrue(p.closure_evidence(d).minimality_passed);self.assertTrue(all(x.passed for x in p.run_controls()))
if __name__=="__main__":unittest.main()
