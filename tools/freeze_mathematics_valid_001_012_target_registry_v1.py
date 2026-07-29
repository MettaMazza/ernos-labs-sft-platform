#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_valid_001_012_target_registry_v1.json"
IDS=("SFT-MATH-VALID-ARITHMETIC-ALGEBRA-001","SFT-MATH-VALID-COMBINATORICS-GRAPH-002","SFT-MATH-VALID-LINEAR-ALGEBRAIC-003","SFT-MATH-VALID-ORDER-GEOMETRY-004","SFT-MATH-VALID-TOPOLOGY-ANALYSIS-005","SFT-MATH-VALID-EQUATION-MEASURE-006","SFT-MATH-VALID-PROBABILITY-STATISTICS-007","SFT-MATH-VALID-OPTIMIZATION-DYNAMICS-008","SFT-MATH-VALID-LOGIC-COMPOSITIONAL-009","SFT-MATH-VALID-NUMERICAL-SYMBOLIC-010","SFT-MATH-VALID-ADVERSE-BOUNDARY-011","SFT-MATH-VALID-EMPIRICAL-FORMAL-GRAND-LOCK-012")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("VALID registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="VALID"]
 if len(obs)!=len(IDS)!=12:raise SystemExit("VALID census changed")
 p={"schema":"sft-v3-mathematics-valid-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected validation result","selected survivor","match result","omitted adverse row","predeclared Grand Lock pass"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
