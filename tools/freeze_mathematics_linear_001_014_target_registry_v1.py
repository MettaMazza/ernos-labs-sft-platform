#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_linear_001_014_target_registry_v1.json"
IDS=("SFT-MATH-LINEAR-VECTOR-COORDINATE-CARRIERS-001","SFT-MATH-LINEAR-MAP-COMPOSITION-002","SFT-MATH-LINEAR-MATRIX-ROW-OPERATIONS-003","SFT-MATH-LINEAR-RANK-NULLITY-004","SFT-MATH-LINEAR-DETERMINANT-ORIENTATION-005","SFT-MATH-LINEAR-EXACT-SYSTEMS-006","SFT-MATH-LINEAR-BASIS-DIMENSION-007","SFT-MATH-LINEAR-INNER-PRODUCT-METRIC-008","SFT-MATH-LINEAR-EIGEN-INVARIANT-SUPPORT-009","SFT-MATH-LINEAR-RATIONAL-SPECTRAL-ENCLOSURE-010","SFT-MATH-LINEAR-MULTILINEAR-TENSOR-PRODUCT-011","SFT-MATH-LINEAR-TENSOR-CONTRACTION-012","SFT-MATH-LINEAR-EXTERIOR-SYMMETRIC-013","SFT-MATH-LINEAR-OPERATOR-DECOMPOSITION-014")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("LINEAR registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="LINEAR"]
 if len(obs)!=len(IDS) or len(IDS)!=14:raise SystemExit("LINEAR census changed")
 p={"schema":"sft-v3-mathematics-linear-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all fourteen claims; no proper subset","prohibited_target_fields":["expected coordinates","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":14,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
