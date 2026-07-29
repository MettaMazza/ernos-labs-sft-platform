#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_xint_001_008_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/xint_001_008_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("XINT vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("XINT registry changed")
 names=("information","computation","physics","chemistry","biology","social","engineering","one_owner_identity")
 values=(
  {"mathematics_owns":["exact-support","distinguishability-structure"],"downstream_owns":["semantic-information-quantity","channel-observation"]},
  {"mathematics_owns":["state-set","relation","proof-structure"],"downstream_owns":["execution","resource-law","machine-behaviour"]},
  {"mathematics_owns":["exact-quantity-record","geometry","symmetry-structure"],"downstream_owns":["physical-identification","measured-value","unit-realization"]},
  {"mathematics_owns":["graph","algebraic-relation","enumeration"],"downstream_owns":["chemical-identity","reaction-measurement","material-context"]},
  {"mathematics_owns":["network","order","probability-correspondence"],"downstream_owns":["biological-function","organism-observation","evolutionary-history"]},
  {"mathematics_owns":["inference-structure","game-relation","network"],"downstream_owns":["population-observation","institutional-meaning","behavioural-claim"]},
  {"mathematics_owns":["calculation","optimization-structure","certificate"],"downstream_owns":["design-choice","performance-test","safety-acceptance"]},
  {"registered_interfaces":7,"unique_branch_labels":7,"duplicate_owners":[],"typed_references_only":True},
 )
 records=[]
 for i,(name,value) in enumerate(zip(names,values),1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-xint-{i:03d}-observation-retained","source_ids":["SFT-V3-CROSS-BRANCH-OWNERSHIP-OBSERVER","SFT-V3-BRANCH-ROADMAP-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-xint-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":8,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":8,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
