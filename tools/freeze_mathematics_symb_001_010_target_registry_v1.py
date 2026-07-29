#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_symb_001_010_target_registry_v1.json"
IDS=(
 "SFT-MATH-SYMB-CANONICAL-EXPRESSION-001",
 "SFT-MATH-SYMB-SIMPLIFICATION-PROVENANCE-002",
 "SFT-MATH-SYMB-POLYNOMIAL-FACTOR-EXPAND-003",
 "SFT-MATH-SYMB-EQUATION-SOLVING-004",
 "SFT-MATH-SYMB-REWRITE-TERMINATION-CONFLUENCE-005",
 "SFT-MATH-SYMB-GENERATING-FUNCTION-TRANSFORM-006",
 "SFT-MATH-SYMB-FOURIER-LAPLACE-CORRESPONDENCE-007",
 "SFT-MATH-SYMB-SPECIAL-FUNCTION-RECURRENCE-008",
 "SFT-MATH-SYMB-THEOREM-SEARCH-BOUNDARY-009",
 "SFT-MATH-SYMB-CONSTRUCTIVE-CERTIFICATE-010",
)
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("SYMB registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="SYMB"]
 if len(obs)!=len(IDS)!=10:raise SystemExit("SYMB census changed")
 p={"schema":"sft-v3-mathematics-symb-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all ten claims; no proper subset","prohibited_target_fields":["expected symbolic result","selected survivor","match result","imported computer-algebra answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":10,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
