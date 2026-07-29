#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_alext_001_010_target_registry_v1.json"
IDS=("SFT-MATH-ALEXT-POLYNOMIAL-ROOT-ISOLATION-001","SFT-MATH-ALEXT-ALGEBRAIC-BALANCE-002","SFT-MATH-ALEXT-EXTENSION-TOWER-003","SFT-MATH-ALEXT-FINITE-FIELD-004","SFT-MATH-ALEXT-GALOIS-ORBIT-005","SFT-MATH-ALEXT-CYCLOTOMIC-CORRESPONDENCE-006","SFT-MATH-ALEXT-HELD-PAIR-COMPLEX-007","SFT-MATH-ALEXT-REAL-ALGEBRAIC-ORDER-008","SFT-MATH-ALEXT-PRIME-ADIC-VALUATION-009","SFT-MATH-ALEXT-TRANSCENDENTAL-BOUNDARY-010")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ALEXT registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="ALEXT"]
 if len(obs)!=len(IDS)!=10:raise SystemExit("ALEXT census changed")
 p={"schema":"sft-v3-mathematics-alext-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all ten claims; no proper subset","prohibited_target_fields":["expected scalar","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":10,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
