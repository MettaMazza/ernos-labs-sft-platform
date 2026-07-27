import importlib.util,json
from pathlib import Path
import pytest
from sft.chemistry.coordination_entity_law_v1 import CompleteCoordinationEntity,RetainedCoordinationAttachment
from sft.chemistry.coordination_number_batch_v1 import COORDINATION_NUMBER_SPEC,IDENTITY_PATH,PRIMARY_PATH,TARGET_PATH
from sft.chemistry.coordination_number_law_v1 import append_incidence_increments_coordination_number,forced_coordination_number
from sft.chemistry.coordination_number_validation_v1 import _source_rows,exact_coordination_number_analysis,prediction_program_document
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
ROOT=Path(__file__).resolve().parents[1]
def entity(width):
 c=HeldLabel("coordination-central-occurrence","central"); rows=tuple(RetainedCoordinationAttachment(PositiveCount(n),c,HeldLabel("coordination-ligand-occurrence",f"L-{n}"),HeldLabel("coordination-ligand-group","L"),HeldLabel("positive-coordination-incidence",f"edge-{n}")) for n in range(1,width+1)); return CompleteCoordinationEntity(HeldLabel("coordination-entity",f"e-{width}"),HeldLabel("coordination-central-element","M"),c,rows)
def test_spec(): assert len(COORDINATION_NUMBER_SPEC.dimensions)==8 and all(len(d.choices)==2 for d in COORDINATION_NUMBER_SPEC.dimensions)
def test_counts(): assert tuple(forced_coordination_number(entity(n)).positive_direct_incidence_count.value for n in (3,4,5))==(3,4,5)
def test_successor():
 e=entity(3); s=RetainedCoordinationAttachment(PositiveCount(4),e.central_occurrence,HeldLabel("coordination-ligand-occurrence","L-4"),HeldLabel("coordination-ligand-group","L"),HeldLabel("positive-coordination-incidence","edge-4")); assert append_incidence_increments_coordination_number(e,s)
def test_mismatch_rejected():
 e=entity(1)
 with pytest.raises(InadmissibleExactValue): append_incidence_increments_coordination_number(e,RetainedCoordinationAttachment(PositiveCount(2),HeldLabel("coordination-central-occurrence","other"),HeldLabel("coordination-ligand-occurrence","L-2"),HeldLabel("coordination-ligand-group","L"),HeldLabel("positive-coordination-incidence","edge-2")))
def test_identity_value_free():
 d=json.loads((ROOT/IDENTITY_PATH).read_text()); assert d["target_values_or_hashes_present"] is False and len(d["rows"])==23
def test_complete_analysis():
 a=exact_coordination_number_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text())); assert a["complete_registered_target_count"]==23 and all(v for k,v in a.items() if k not in {"complete_registered_target_count","source_class_census"})
def test_prediction_has_no_long_target_content():
 text=json.dumps(prediction_program_document(ROOT),sort_keys=True); targets=json.loads((ROOT/TARGET_PATH).read_text()); assert all(row["source_inscription"] not in text for row in targets["rows"] if len(row["source_inscription"])>12)
def test_execution_and_dependencies():
 p=ROOT/"claims/SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002/execution.py"; s=importlib.util.spec_from_file_location("inorg002",p); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);admitted={r["claim_id"] for r in json.loads((ROOT/"census/claims.json").read_text())["claims"]};assert set(COORDINATION_NUMBER_SPEC.dependencies)<=admitted and e.program.registration.claim_id==COORDINATION_NUMBER_SPEC.claim_id
