#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_calc_001_012_target_registry_v1.json"
IDS=("SFT-MATH-CALC-FINITE-DIFFERENCE-001","SFT-MATH-CALC-HIGHER-DIFFERENCE-DEGREE-002","SFT-MATH-CALC-ACCUMULATION-SUMS-003","SFT-MATH-CALC-DIFFERENCE-ACCUMULATION-004","SFT-MATH-CALC-PRODUCT-COMPOSITION-LAWS-005","SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006","SFT-MATH-CALC-DERIVATIVE-SHRINKING-PARTS-007","SFT-MATH-CALC-INTEGRAL-REFINEMENT-SUMS-008","SFT-MATH-CALC-MULTIVARIABLE-DIRECTIONAL-009","SFT-MATH-CALC-DIVERGENCE-FLUX-010","SFT-MATH-CALC-VARIATIONAL-STATIONARY-011","SFT-MATH-CALC-CONTINUUM-LIMIT-BOUNDARY-012")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("CALC registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="CALC"]
 if len(obs)!=len(IDS) or len(IDS)!=12:raise SystemExit("CALC census changed")
 p={"schema":"sft-v3-mathematics-calc-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected difference value","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
