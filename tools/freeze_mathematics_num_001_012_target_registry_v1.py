#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_num_001_012_target_registry_v1.json"
IDS=(
 "SFT-MATH-NUM-EXACT-REPRESENTATION-ROUNDING-001",
 "SFT-MATH-NUM-INTERVAL-RATIONAL-ENCLOSURE-002",
 "SFT-MATH-NUM-TRUNCATION-DISCRETIZATION-ERROR-003",
 "SFT-MATH-NUM-FORWARD-BACKWARD-STABILITY-004",
 "SFT-MATH-NUM-CONDITIONING-SENSITIVITY-005",
 "SFT-MATH-NUM-CONVERGENCE-ORDER-BOUND-006",
 "SFT-MATH-NUM-ROOT-ISOLATION-EQUATION-SOLVING-007",
 "SFT-MATH-NUM-LINEAR-SYSTEM-SOLVERS-008",
 "SFT-MATH-NUM-INTERPOLATION-APPROXIMATION-009",
 "SFT-MATH-NUM-QUADRATURE-ACCUMULATION-010",
 "SFT-MATH-NUM-DIFFERENTIAL-EQUATION-CORRESPONDENCE-011",
 "SFT-MATH-NUM-VERIFIED-COMPUTATION-CERTIFICATE-012",
)
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("NUM registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="NUM"]
 if len(obs)!=len(IDS)!=12:raise SystemExit("NUM census changed")
 p={"schema":"sft-v3-mathematics-num-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected numerical result","selected survivor","match result","imported numerical-analysis theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
