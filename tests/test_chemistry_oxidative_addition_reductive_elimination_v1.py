import importlib.util,json
from pathlib import Path
import pytest
from sft.chemistry.oxidative_addition_reductive_elimination_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.oxidative_addition_reductive_elimination_law_v1 import OPERATIONAL_WITNESSES,oxidative_addition,reductive_elimination
from sft.chemistry.oxidative_addition_reductive_elimination_validation_v1 import _source_rows,exact_analysis,prediction_program_document
from sft.engine.exact import InadmissibleExactValue
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[1]
def test_inorg_012_law_and_grammar():
 assert all(x[2] for x in OPERATIONAL_WITNESSES) and len(OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.dimensions)==8
 one=oxidative_addition(("M",),"X","Y"); two=oxidative_addition(("M1","M2"),"X","Y"); assert tuple(x.value for x in one.transfer_distribution)==(2,) and tuple(x.value for x in two.transfer_distribution)==(1,1) and reductive_elimination(one).restored_bond==one.source_bond
 with pytest.raises(InadmissibleExactValue): oxidative_addition(("M1","M2","M3"),"X","Y")
def test_inorg_012_identity_targets(): assert hash_file(ROOT/IDENTITY_PATH)==IDENTITY_HASH and hash_file(ROOT/TARGET_PATH)==TARGET_HASH and hash_file(ROOT/PRIMARY_PATH)==PRIMARY_HASH
def test_inorg_012_external():
 a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text())); assert a["complete_target_count"]==5 and a["complete_source_count"]==2 and a["scope_distinction_count"]==1 and a["all_rows_preserved"]
def test_inorg_012_target_free_survivor():
 doc=prediction_program_document(ROOT); assert "two-electron loss" not in json.dumps(doc,sort_keys=True); p=ROOT/"claims/SFT-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012/execution.py"; s=importlib.util.spec_from_file_location("i12",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); e=m.build_execution(ROOT); c=e.program.generate_candidates(); d=tuple(e.program.decide_candidate(x) for x in c.candidates); assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and all(x.passed for x in e.program.run_controls())
