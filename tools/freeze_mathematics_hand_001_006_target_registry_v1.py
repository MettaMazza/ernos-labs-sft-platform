#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_hand_001_006_target_registry_v1.json"
IDS=("SFT-MATH-HAND-DOWNSTREAM-ONE-OWNER-001","SFT-MATH-HAND-MEASUREMENT-BOUNDARY-002","SFT-MATH-HAND-FORMAL-EMPIRICAL-003","SFT-MATH-HAND-CONVENTIONAL-CORRESPONDENCE-004","SFT-MATH-HAND-OPEN-EXTENSION-005","SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("HAND registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="HAND"]
 if len(obs)!=len(IDS)!=6:raise SystemExit("HAND census changed")
 p={"schema":"sft-v3-mathematics-hand-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all six claims; no proper subset","prohibited_target_fields":["selected downstream result","predeclared branch pass","duplicated owner","permanent closure"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":6,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
