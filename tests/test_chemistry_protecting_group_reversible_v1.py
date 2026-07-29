import importlib.util
from pathlib import Path
import pytest
from sft.chemistry.protecting_group_reversible_law_v1 import DIMENSIONS,OPERATIONAL_WITNESSES
from sft.chemistry.protecting_group_reversible_validation_v1 import exact_analysis
ROOT=Path(__file__).resolve().parents[1]
def test_native():assert len(DIMENSIONS)==8 and len(OPERATIONAL_WITNESSES)==10 and all(x[2] for x in OPERATIONAL_WITNESSES)
def test_external():a,c=exact_analysis(ROOT);assert len(c)==5 and all(c.values()) and a["complete_iupac_record_count"]==2 and a["narrow_deprotection_scope_preserved"]
def test_omission():
 with pytest.raises(ValueError):exact_analysis(ROOT,True)
def test_execution():
 p=ROOT/"claims/SFT-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015/execution.py";s=importlib.util.spec_from_file_location("org015",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);c=e.program.generate_candidates();assert len(c.candidates)==256 and sum(e.program.decide_candidate(x).survives for x in c.candidates)==1 and all(x.passed for x in e.program.run_controls())
