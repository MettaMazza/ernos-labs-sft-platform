import importlib.util
from pathlib import Path
import pytest
from sft.chemistry.retrosynthetic_reconstruction_law_v1 import DIMENSIONS,OPERATIONAL_WITNESSES
from sft.chemistry.retrosynthetic_reconstruction_validation_v1 import exact_analysis
ROOT=Path(__file__).resolve().parents[1]
def test_native():assert len(DIMENSIONS)==8 and len(OPERATIONAL_WITNESSES)==10 and all(x[2] for x in OPERATIONAL_WITNESSES)
def test_external():a,c=exact_analysis(ROOT);assert len(c)==7 and all(c.values()) and (a["four_leaf_complete_tree_count"],a["five_leaf_successor_tree_count"])==(5,14)
def test_omission():
 with pytest.raises(ValueError):exact_analysis(ROOT,True)
def test_execution():
 p=ROOT/"claims/SFT-CHEM-RETROSYNTHETIC-DECOMPOSITION-RECONSTRUCTION-016/execution.py";s=importlib.util.spec_from_file_location("org016",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);c=e.program.generate_candidates();assert len(c.candidates)==256 and sum(e.program.decide_candidate(x).survives for x in c.candidates)==1 and all(x.passed for x in e.program.run_controls())
