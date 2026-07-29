#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_dyn_001_012_target_registry_v1.json"
IDS=("SFT-MATH-DYN-STATE-ORBIT-001","SFT-MATH-DYN-FIXED-PERIODIC-002","SFT-MATH-DYN-RECURRENCE-RETURN-003","SFT-MATH-DYN-INVARIANT-CONSERVED-004","SFT-MATH-DYN-STABILITY-ATTRACTION-005","SFT-MATH-DYN-BIFURCATION-DISTINCTION-006","SFT-MATH-DYN-SYMBOLIC-SHIFT-007","SFT-MATH-DYN-EXACT-SENSITIVITY-008","SFT-MATH-DYN-ERGODIC-AVERAGE-009","SFT-MATH-DYN-HAMILTONIAN-REVERSIBLE-010","SFT-MATH-DYN-DISSIPATIVE-RETAINED-LOSS-011","SFT-MATH-DYN-COUPLED-NETWORKED-012")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("DYN registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="DYN"]
 if len(obs)!=len(IDS)!=12:raise SystemExit("DYN census changed")
 p={"schema":"sft-v3-mathematics-dyn-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected orbit","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
