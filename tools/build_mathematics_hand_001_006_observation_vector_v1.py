#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_hand_001_006_target_registry_v1.json";REC=ROOT/"census/mathematics_discipline_current_reconciliation_v22.json";OUT=ROOT/"experiments/external_sources/mathematics/hand_001_006_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("HAND vector already frozen")
 r=json.loads(REG.read_text());rb=dict(r);ri=rb.pop("registry_identity");rec=json.loads(REC.read_text());rc=dict(rec);rci=rc.pop("reconciliation_identity")
 if canon(rb)!=ri or canon(rc)!=rci or r["target_content_present"] is not False or rec["current_closed_count"]!=317:raise SystemExit("HAND frozen predecessor changed")
 values=(
  {"mathematics_owner":"exact-structure-and-proof-relation","downstream_mode":"typed-reference","ownership_transfer":False,"duplicate_owner":False},
  {"mathematics_owns":"exact-representation","empirical_branch_owns":["physical-identification","unit-realization","measurement","uncertainty"],"boundary_explicit":True},
  {"formal_record":"root-bound-derivation-and-certificate","empirical_record":"post-seal-observation-and-comparison","joined_only_by_registered_target":True},
  {"conventional_term_role":"comparison-and-translation","premise_role":False,"correspondence_must_preserve_SFT_boundary":True},
  {"completion":"dated-current-census","lawful_extension_open":True,"permanent_lock":False,"new_claim_requires_full_protocol":True},
  {"pre_handoff_closed":317,"registered_handoff_obligations":6,"expected_post_handoff_total":323,"frozen_census_total":323,"single_owner_required":True},
 )
 names=("downstream_one_owner","measurement_boundary","formal_empirical","conventional_correspondence","open_extension","cross_branch_completeness")
 records=[]
 for i,(name,value) in enumerate(zip(names,values),1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-hand-{i:03d}-observation-retained","source_ids":["census/mathematics_discipline_current_reconciliation_v22.json","census/mathematics_discipline_obligations.json","docs/branch_roadmaps/README.md"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-hand-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"pre_handoff_reconciliation_identity":rci,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":6,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":6,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
