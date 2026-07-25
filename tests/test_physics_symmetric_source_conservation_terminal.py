import json
from pathlib import Path
import unittest
from sft.physics.symmetric_source_conservation_terminal_law_v1 import SymmetricSourceConservationProgram,candidate_forms,conservation_certificate,form_survives,source_component_ledger,symmetric_slots
from sft.physics.symmetric_source_conservation_terminal_validation_v1 import authoritative_record,exact_measurement_analysis,experiment_registration_record
ROOT=Path(__file__).resolve().parents[1]
class SymmetricSourceConservationTests(unittest.TestCase):
 def test_exact_component_and_conservation_law(self):
  c=conservation_certificate();self.assertEqual(len(symmetric_slots()),10);self.assertEqual(tuple(len(v) for v in source_component_ledger().values()),(1,3,6));self.assertEqual(len(c["conserved_directions"]),4);self.assertTrue(c["all_four_balanced"]);self.assertEqual({(r["carried_terms"],r["opposed_terms"],r["distinct_terms"]) for r in c["divergence_rows"]},{(48,48,31)});self.assertTrue(c["commutation"]["every_derivative_order_commutes"]);self.assertFalse(c["leaking_control_balanced"]);self.assertTrue(c["leaking_control_has_one_missing_flow"])
 def test_complete_census(self):
  forms=candidate_forms();survivors=tuple(form for form in forms if form_survives(form));self.assertEqual(len(forms),2916);self.assertEqual(len({form.candidate_id for form in forms}),2916);self.assertEqual(len(survivors),1)
 def test_formal_target_absence(self):
  text=(ROOT/"sft/physics/symmetric_source_conservation_terminal_law_v1.py").read_text()
  for forbidden in ("Bianchi","Einstein","Carroll","LIGO","Regge","20.81","23.09","source-record","expected_survivor",'"admitted": true'):
   self.assertNotIn(forbidden,text)
 def test_postseal_complete_comparison(self):
  analysis=exact_measurement_analysis(authoritative_record(ROOT)["registered_target"]);self.assertTrue(analysis["historical_counts_match"]);self.assertTrue(analysis["existing_v3_counts_match"]);self.assertTrue(analysis["regge_scope_preserved"]);self.assertTrue(analysis["ligo_scope_preserved"]);self.assertTrue(analysis["all_target_rows_retained"]);self.assertFalse(analysis["fitted_value_used"])
 def test_registration_and_program(self):
  registration=json.loads(json.dumps(experiment_registration_record()));self.assertEqual(len(registration["source_hashes"]),6);program=SymmetricSourceConservationProgram("sha256:test");census=program.generate_candidates();decisions=tuple(program.decide_candidate(candidate) for candidate in census.candidates);self.assertTrue(program.closure_evidence(decisions).minimality_passed);self.assertTrue(all(control.passed for control in program.run_controls()))
if __name__=="__main__":unittest.main()
