#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_alg_001_016_target_registry_v1.json"
IDS=("SFT-MATH-ALG-MAGMA-CLOSED-OPERATION-001","SFT-MATH-ALG-SEMIGROUP-ASSOCIATIVITY-002","SFT-MATH-ALG-MONOID-IDENTITY-003","SFT-MATH-ALG-GROUP-HELD-INVERSE-004","SFT-MATH-ALG-PERMUTATION-GROUP-ACTION-005","SFT-MATH-ALG-QUOTIENT-NORMAL-SUBSTRUCTURE-006","SFT-MATH-ALG-RING-DISTRIBUTIVE-007","SFT-MATH-ALG-INTEGRAL-DOMAIN-008","SFT-MATH-ALG-FIELD-EXACT-DIVISION-009","SFT-MATH-ALG-MODULE-SCALAR-ACTION-010","SFT-MATH-ALG-COMPATIBLE-ALGEBRA-PRODUCT-011","SFT-MATH-ALG-IDEAL-QUOTIENT-012","SFT-MATH-ALG-REPRESENTATION-ACTION-DECOMPOSITION-013","SFT-MATH-ALG-EXACT-SEQUENCE-HOMOLOGICAL-014","SFT-MATH-ALG-UNIVERSAL-IDENTITIES-015","SFT-MATH-ALG-OPERADIC-COMPOSITION-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ALG registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="ALG"]
 if len(obs)!=len(IDS) or len(IDS)!=16:raise SystemExit("ALG census changed")
 p={"schema":"sft-v3-mathematics-alg-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected table","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
