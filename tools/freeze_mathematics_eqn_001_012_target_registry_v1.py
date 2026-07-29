#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_eqn_001_012_target_registry_v1.json"
IDS=("SFT-MATH-EQN-ORDINARY-DIFFERENCE-001","SFT-MATH-EQN-ORDINARY-DIFFERENTIAL-002","SFT-MATH-EQN-PARTIAL-DIFFERENCE-003","SFT-MATH-EQN-PARTIAL-DIFFERENTIAL-004","SFT-MATH-EQN-BOUNDARY-INITIAL-WELL-POSED-005","SFT-MATH-EQN-INTEGRAL-CORRESPONDENCE-006","SFT-MATH-EQN-FUNCTIONAL-STRUCTURE-007","SFT-MATH-EQN-RECURRENCE-SOLUTION-SPACE-008","SFT-MATH-EQN-GREEN-RESPONSE-009","SFT-MATH-EQN-CONSERVATION-WEAK-010","SFT-MATH-EQN-STABILITY-PERTURBATION-011","SFT-MATH-EQN-EXISTENCE-UNIQUENESS-BLOWUP-012")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("EQN registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="EQN"]
 if len(obs)!=len(IDS) or len(IDS)!=12:raise SystemExit("EQN census changed")
 p={"schema":"sft-v3-mathematics-eqn-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected solution value","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
