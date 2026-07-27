import importlib.util,json
from pathlib import Path
import pytest
from sft.chemistry.metal_cluster_bonding_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,METAL_CLUSTER_BONDING_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.metal_cluster_bonding_law_v1 import OPERATIONAL_WITNESSES,append_centre,forced_cluster,relation
from sft.chemistry.metal_cluster_bonding_validation_v1 import _source_rows,exact_analysis,prediction_program_document
from sft.engine.exact import InadmissibleExactValue,PositiveCount
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[1]
def test_inorg_014_law():
 assert all(x[2] for x in OPERATIONAL_WITNESSES) and len(METAL_CLUSTER_BONDING_SPEC.dimensions)==8;b=forced_cluster("b",("M1","M2"),(relation("M1","M2","bridging-ligand-path",PositiveCount(2)),));assert append_centre(b,"M3","M2","held-grouping-relation").centre_count.value==3
 with pytest.raises(InadmissibleExactValue):forced_cluster("x",("M1","M2","M3"),(relation("M1","M2","direct-metal-bond"),))
def test_inorg_014_hashes():assert hash_file(ROOT/IDENTITY_PATH)==IDENTITY_HASH and hash_file(ROOT/TARGET_PATH)==TARGET_HASH and hash_file(ROOT/PRIMARY_PATH)==PRIMARY_HASH
def test_inorg_014_external():
 a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text()));assert a["complete_target_count"]==10 and a["complete_source_count"]==2 and a["charge_inscription_surface_count"]==1 and a["all_rows_preserved"]
def test_inorg_014_survivor():
 doc=prediction_program_document(ROOT);assert "[4\\! Fe-4\\! S]" not in json.dumps(doc,sort_keys=True);p=ROOT/"claims/SFT-CHEM-METAL-CLUSTER-BONDING-014/execution.py";s=importlib.util.spec_from_file_location("i14",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);c=e.program.generate_candidates();d=tuple(e.program.decide_candidate(x) for x in c.candidates);assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and all(x.passed for x in e.program.run_controls())
