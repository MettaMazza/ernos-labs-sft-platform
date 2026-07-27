import importlib.util,json
from pathlib import Path
from sft.chemistry.insertion_elimination_pathway_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,INSERTION_ELIMINATION_PATHWAY_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.insertion_elimination_pathway_law_v1 import OPERATIONAL_WITNESSES,elimination,extrusion,insertion,migratory_insertion
from sft.chemistry.insertion_elimination_pathway_validation_v1 import _source_rows,exact_analysis,prediction_program_document
from sft.engine.source import hash_file
ROOT=Path(__file__).resolve().parents[1]
def test_inorg_013_law():
 assert all(x[2] for x in OPERATIONAL_WITNESSES) and len(INSERTION_ELIMINATION_PATHWAY_SPEC.dimensions)==8;ins=insertion("X","Z","Y");assert (len(ins.before),len(ins.after),len(ins.removed),len(ins.added))==(1,2,1,2) and extrusion(ins).after==ins.before and tuple(x.label for x in migratory_insertion("M","X","Y").composition)==("migration","insertion") and len(elimination("A","A","X","Y").carriers)==3
def test_inorg_013_identity():assert hash_file(ROOT/IDENTITY_PATH)==IDENTITY_HASH and hash_file(ROOT/TARGET_PATH)==TARGET_HASH and hash_file(ROOT/PRIMARY_PATH)==PRIMARY_HASH
def test_inorg_013_external():
 a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text()));assert a["complete_target_count"]==10 and a["complete_source_count"]==3 and a["scope_distinction_count"]==1 and a["rendered_structure_absence_count"]==1 and a["all_rows_preserved"]
def test_inorg_013_target_free_survivor():
 doc=prediction_program_document(ROOT);assert "X-Z + Y -> X-Y-Z" not in json.dumps(doc,sort_keys=True);p=ROOT/"claims/SFT-CHEM-INSERTION-ELIMINATION-PATHWAY-013/execution.py";s=importlib.util.spec_from_file_location("i13",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);c=e.program.generate_candidates();d=tuple(e.program.decide_candidate(x) for x in c.candidates);assert len(c.candidates)==256 and sum(x.survives for x in d)==1 and all(x.passed for x in e.program.run_controls())
