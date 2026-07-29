import json
from pathlib import Path
from sft.mathematics.arith_001_018_external_v1 import load
from sft.mathematics.arith_001_018_laws_v1 import IDS,OBS,SPECS
from sft.mathematics.generated_law import candidate_records,survivor_id
ROOT=Path(__file__).resolve().parents[1]
def test_complete_whole_family_specs_and_products():
 assert len(IDS)==len(SPECS)==18
 for spec in SPECS.values():
  spec.validate();rows=candidate_records(spec);assert len(rows)==len({x["candidate_id"] for x in rows})==256;assert sum(x["candidate_id"]==survivor_id(spec) for x in rows)==1
def test_all_exact_operational_observations_pass():assert len(OBS)==18 and all(value for _,value in OBS.values())
def test_value_free_registry_and_post_registry_vector():
 registry,vector=load(ROOT);assert registry["target_content_present"] is False;assert len(registry["claim_ids"])==vector["record_count"]==18;assert vector["outcomes_opened_only_after_registry_freeze"] is True
def test_vector_membership_and_all_row_custody():
 registry,vector=load(ROOT);assert tuple(x["claim_id"] for x in vector["records"])==tuple(registry["claim_ids"]);assert all(x["all_rows_preserved"] and x["source_ids"] and x["exact_observation"] is not None for x in vector["records"])
