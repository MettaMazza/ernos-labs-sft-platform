from pathlib import Path
from sft.mathematics.cat_001_012_external_v1 import load
from sft.mathematics.cat_001_012_laws_v1 import IDS,OBS,SPECS
from sft.mathematics.generated_law import candidate_records,survivor_id
ROOT=Path(__file__).resolve().parents[1]
def test_complete_family_products():
 assert len(IDS)==len(SPECS)==12
 for s in SPECS.values():s.validate();rows=candidate_records(s);assert len(rows)==len({x["candidate_id"] for x in rows})==256;assert sum(x["candidate_id"]==survivor_id(s) for x in rows)==1
def test_observations():assert len(OBS)==12 and all(v for _,v in OBS.values())
def test_registry_vector():
 r,v=load(ROOT);assert r["target_content_present"] is False;assert len(r["claim_ids"])==v["record_count"]==12;assert v["outcomes_opened_only_after_registry_freeze"]
def test_membership_and_custody():
 r,v=load(ROOT);assert tuple(x["claim_id"] for x in v["records"])==tuple(r["claim_ids"]);assert all(x["all_rows_preserved"] and x["source_ids"] for x in v["records"])
