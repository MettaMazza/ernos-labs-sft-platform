import json
from pathlib import Path
import unittest
from sft.physics.lyapunov_ks_correspondence_terminal_law_v1 import LyapunovKSCorrespondenceProgram,candidate_forms,carrier_certificate,exact_support_count,form_survives,separation_carrier
from sft.physics.lyapunov_ks_correspondence_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record

ROOT=Path(__file__).resolve().parents[1]
class LyapunovKSCorrespondenceTests(unittest.TestCase):
 def test_general_exact_carrier(self):
  for m in (2,3,5,7):
   self.assertEqual(tuple(exact_support_count(m,d) for d in (1,2,3,4)),tuple(m**d for d in (1,2,3,4)))
   self.assertEqual(tuple(separation_carrier(m,p)//p for p in (1,2,3,5)),(m,m,m,m))
  self.assertTrue(carrier_certificate()["common_exact_carrier"])
 def test_complete_census(self):
  forms=candidate_forms(); survivors=tuple(form for form in forms if form_survives(form)); self.assertEqual(len(forms),2916); self.assertEqual(len({x.candidate_id for x in forms}),2916); self.assertEqual(len(survivors),1)
 def test_formal_target_absence_and_no_self_admission(self):
  text=(ROOT/"sft/physics/lyapunov_ks_correspondence_terminal_law_v1.py").read_text()
  for forbidden in ("arxiv","source-record","expected_survivor",'"admitted": true',"natural-logarithm-of-two","one-bit-per-step","1211.1234","1004.3441"):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  analysis=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"])
  self.assertEqual(analysis["complete_support"],(2,4,8,16,32)); self.assertTrue(analysis["all_exact_carriers_equal"]); self.assertFalse(analysis["analytic_value_computed_or_imported"])
 def test_registration_and_program(self):
  reg=json.loads(json.dumps(experiment_registration_record())); self.assertEqual(len(reg["source_hashes"]),3)
  program=LyapunovKSCorrespondenceProgram("sha256:test"); census=program.generate_candidates(); decisions=tuple(program.decide_candidate(x) for x in census.candidates); self.assertTrue(program.closure_evidence(decisions).minimality_passed); self.assertTrue(all(x.passed for x in program.run_controls()))
if __name__=="__main__": unittest.main()
