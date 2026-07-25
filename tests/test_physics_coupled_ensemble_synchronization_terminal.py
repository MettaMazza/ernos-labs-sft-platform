from fractions import Fraction
import json
from pathlib import Path
import unittest
from sft.physics.coupled_ensemble_synchronization_terminal_law_v1 import CoupledEnsembleSynchronizationProgram,candidate_forms,form_survives,formal_certificate,residual_record
from sft.physics.coupled_ensemble_synchronization_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record

ROOT=Path(__file__).resolve().parents[1]
class CoupledEnsembleSynchronizationTests(unittest.TestCase):
 def test_unique_pair_boundary(self):
  for pair in ((Fraction(1,8),Fraction(7,8)),(Fraction(1,4),Fraction(3,4)),(Fraction(1,3),Fraction(2,3))):
   self.assertEqual(residual_record(*pair,Fraction(1,2)),())
   self.assertGreater(residual_record(*pair,Fraction(1,3))[0],0)
   self.assertGreater(residual_record(*pair,Fraction(2,3))[0],0)
 def test_complete_census(self):
  forms=candidate_forms(); survivors=tuple(form for form in forms if form_survives(form)); self.assertEqual(len(forms),2916); self.assertEqual(len({x.candidate_id for x in forms}),2916); self.assertEqual(len(survivors),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/coupled_ensemble_synchronization_terminal_law_v1.py").read_text()
  for forbidden in ("SFTOM-V1","source-record","expected_survivor",'"admitted": true',"Fraction(i,21)","range(15)","(12,10,7,5,4,3,2,1"):
   self.assertNotIn(forbidden,text)
  self.assertTrue(formal_certificate()["synchronized_terminal_preserved"])
 def test_postseal_full_recurrence(self):
  analysis=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"])
  self.assertEqual(analysis["final_region_counts"],(7,7,1,5,5)); self.assertEqual(analysis["half_One_recurrence"],(12,10,7,5,4,3,2,1,1,1,1,1,1,1,1)); self.assertEqual(analysis["half_One_terminal_point"],Fraction(4,7)); self.assertTrue(analysis["half_One_uniquely_reaches_one_region"])
 def test_registration_and_program(self):
  reg=json.loads(json.dumps(experiment_registration_record())); self.assertEqual(len(reg["source_hashes"]),3)
  program=CoupledEnsembleSynchronizationProgram("sha256:test"); census=program.generate_candidates(); decisions=tuple(program.decide_candidate(x) for x in census.candidates); self.assertTrue(program.closure_evidence(decisions).minimality_passed); self.assertTrue(all(x.passed for x in program.run_controls()))
if __name__=="__main__": unittest.main()
