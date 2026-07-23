import importlib.util,unittest
from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.form_grammar import CLAIM_ID,SURVIVOR,candidate_records,generated_examples,valid_form
def load():
 p=ROOT/"claims"/CLAIM_ID/"execution.py";s=importlib.util.spec_from_file_location("fg",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
class T(unittest.TestCase):
 def test_grammar_product(self):self.assertEqual(len(candidate_records()),288)
 def test_examples(self):self.assertTrue(all(valid_form(x) for x in generated_examples()))
 def test_survivor(self):
  e=load();c=e.program.generate_candidates();d=[e.program.decide_candidate(x) for x in c.candidates];self.assertEqual([x.candidate_id for x in d if x.survives],[SURVIVOR])
 def test_engine(self):
  e=load();self.assertTrue(EngineRepository(ROOT).engine.run(e.program,e.independent_validator).model_admitted)
if __name__=="__main__":unittest.main()
