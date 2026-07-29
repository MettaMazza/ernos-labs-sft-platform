#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_xint_001_008_target_registry_v1.json"
IDS=("SFT-MATH-XINT-INFORMATION-HANDOFF-001","SFT-MATH-XINT-COMPUTATION-HANDOFF-002","SFT-MATH-XINT-PHYSICS-HANDOFF-003","SFT-MATH-XINT-CHEMISTRY-HANDOFF-004","SFT-MATH-XINT-BIOLOGY-HANDOFF-005","SFT-MATH-XINT-SOCIAL-HANDOFF-006","SFT-MATH-XINT-ENGINEERING-HANDOFF-007","SFT-MATH-XINT-ONE-OWNER-IDENTITY-008")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("XINT registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="XINT"]
 if len(obs)!=len(IDS)!=8:raise SystemExit("XINT census changed")
 p={"schema":"sft-v3-mathematics-xint-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all eight claims; no proper subset","prohibited_target_fields":["selected downstream result","duplicated owner","match result","imported branch conclusion"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":8,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
