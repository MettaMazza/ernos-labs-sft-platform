#!/usr/bin/env python3
"""Freeze value-free identities for the whole ARITH-001--018 family."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"census/mathematics_arith_001_018_target_registry_v1.json"
IDS=(
"SFT-MATH-ARITH-GENERATED-SUCCESSION-001","SFT-MATH-ARITH-JUNCTION-ADDITION-002",
"SFT-MATH-ARITH-PAIR-CELL-MULTIPLICATION-003","SFT-MATH-ARITH-DIVISIBILITY-GCD-LCM-004",
"SFT-MATH-ARITH-QUOTIENT-REMAINDER-005","SFT-MATH-ARITH-PRIME-IRREDUCIBLE-006",
"SFT-MATH-ARITH-UNIQUE-FACTORIZATION-007","SFT-MATH-ARITH-CANONICAL-FRACTION-008",
"SFT-MATH-ARITH-CONTINUED-FRACTION-009","SFT-MATH-ARITH-CONGRUENCE-010",
"SFT-MATH-ARITH-COMPATIBLE-CONGRUENCE-011","SFT-MATH-ARITH-VALUATION-012",
"SFT-MATH-ARITH-DIOPHANTINE-ENUMERATION-013","SFT-MATH-ARITH-RECURRENCE-SEQUENCE-014",
"SFT-MATH-ARITH-GENERATING-FUNCTION-015","SFT-MATH-ARITH-PARTITION-COMPOSITION-016",
"SFT-MATH-ARITH-ARITHMETIC-FUNCTIONS-017","SFT-MATH-ARITH-PRIME-DISTRIBUTION-ENCLOSURE-018",
)
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("Mathematics ARITH target registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text()); obligations=[x for x in census["obligations"] if x["family"]=="ARITH"]
 if len(obligations)!=len(IDS)!=18 or census["target_content_present"] is not False:raise SystemExit("ARITH census boundary changed")
 payload={"schema":"sft-v3-mathematics-arith-001-018-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obligations],"question_titles":[x["title"] for x in obligations],"completion_unit":"all eighteen claims; no proper subset","prohibited_target_fields":["expected value","selected survivor","match result","measurement outcome","imported theorem answer"]}
 payload["registry_identity"]=canonical(payload);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":18,"identity":payload["registry_identity"],"path":OUT.relative_to(ROOT).as_posix()},indent=2))
if __name__=="__main__":main()
