import importlib.util,unittest
from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.fold_assembly import CLAIM_ID,SURVIVOR,candidate_records,support_after_extensions
def load():
 p=ROOT/"claims"/CLAIM_ID/"execution.py";s=importlib.util.spec_from_file_location("fa",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
class T(unittest.TestCase):
 def test_grammar(self):self.assertEqual(len(candidate_records()),192)
 def test_support(self):self.assertEqual([len(support_after_extensions(x)) for x in range(1,6)],[2,4,8,16,32])
 def test_survivor(self):
  e=load();c=e.program.generate_candidates();d=[e.program.decide_candidate(x) for x in c.candidates];self.assertEqual([x.candidate_id for x in d if x.survives],[SURVIVOR])
 def test_engine(self):self.assertTrue(EngineRepository(ROOT).engine.run(load().program,load().independent_validator).model_admitted)
if __name__=="__main__":unittest.main()
