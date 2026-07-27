import importlib.util,json
from pathlib import Path
import pytest
from sft.chemistry.organometallic_electron_accounting_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.organometallic_electron_accounting_law_v1 import OPERATIONAL_WITNESSES,append_pair,complete_pairs,forced_electron_account,forced_spd_capacity
from sft.chemistry.organometallic_electron_accounting_validation_v1 import _source_rows,exact_analysis,prediction_program_document
from sft.claim_evidence import EmptyOne
from sft.engine.exact import InadmissibleExactValue,PositiveCount
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[1]
def test_inorg_011_exact_law_and_grammar():
 assert all(x[2] for x in OPERATIONAL_WITNESSES); assert len(ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC.dimensions)==8; assert forced_spd_capacity().value==18
 complete=forced_electron_account("complete",complete_pairs("n",PositiveCount(4)),complete_pairs("b",PositiveCount(5))); assert complete.complete_electron_count.value==18 and complete.capacity_relation.label=="capacity-complete"
 with pytest.raises(InadmissibleExactValue): append_pair(complete,"bond")
def test_inorg_011_identity_and_targets():
 assert hash_file(ROOT/IDENTITY_PATH)==IDENTITY_HASH and hash_file(ROOT/TARGET_PATH)==TARGET_HASH and hash_file(ROOT/PRIMARY_PATH)==PRIMARY_HASH
 assert json.loads((ROOT/IDENTITY_PATH).read_text())["target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"] is False
def test_inorg_011_external_vector():
 a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text())); assert (a["s_width"],a["p_width"],a["d_width"],a["capacity"])==(2,6,10,18); assert a["complete_target_count"]==4 and a["all_rows_preserved"]
def test_inorg_011_target_free_one_survivor():
 doc=prediction_program_document(ROOT); encoded=json.dumps(doc,sort_keys=True); assert "should be 18" not in encoded and "target_payload_hash" not in encoded
 p=ROOT/"claims/SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011/execution.py"; s=importlib.util.spec_from_file_location("inorg011_test",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); e=m.build_execution(ROOT); c=e.program.generate_candidates(); d=tuple(e.program.decide_candidate(x) for x in c.candidates); assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and all(x.passed for x in e.program.run_controls())
