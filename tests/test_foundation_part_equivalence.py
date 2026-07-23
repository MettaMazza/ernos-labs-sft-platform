"""Checks for generated common-refinement part equivalence."""
from dataclasses import replace
import importlib.util, unittest
from sft.cli import ROOT
from sft.engine import EngineRepository
from sft.foundation.part_equivalence import CLAIM_ID, SURVIVOR, candidate_records
def load_execution():
    p=ROOT/"claims"/CLAIM_ID/"execution.py"; s=importlib.util.spec_from_file_location("peq_test",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.build_execution(ROOT)
class PartEquivalenceTests(unittest.TestCase):
    def test_complete_witness_grammar(self):
        c=load_execution().program.generate_candidates(); self.assertEqual(len(c.candidates),1024); self.assertEqual(c.expected_cardinality,len(candidate_records()))
    def test_unique_witness(self):
        e=load_execution(); c=e.program.generate_candidates(); d=tuple(e.program.decide_candidate(x) for x in c.candidates); self.assertEqual([x.candidate_id for x in d if x.survives],[SURVIVOR])
    def test_engine_and_independent_validator(self):
        e=load_execution(); r=EngineRepository(ROOT).engine.run(e.program,e.independent_validator); self.assertTrue(r.model_admitted)
    def test_tampered_second_survivor_rejected(self):
        e=load_execution(); box={}
        class C:
            def validate(self,sealed): box["s"]=sealed; return e.independent_validator.validate(sealed)
        EngineRepository(ROOT).engine.run(e.program,C()); s=box["s"]; ds=list(s.decisions); ds[0]=replace(ds[0],survives=True); self.assertFalse(e.independent_validator.validate(replace(s,decisions=tuple(ds))).passed)
if __name__=="__main__": unittest.main()
