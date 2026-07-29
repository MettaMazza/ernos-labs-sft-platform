#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_logic_001_016_target_registry_v1.json"
IDS=("SFT-MATH-LOGIC-PROPOSITION-DISTINCTION-001","SFT-MATH-LOGIC-INFERENCE-CONSEQUENCE-002","SFT-MATH-LOGIC-SOUND-COMPLETE-CORRESPONDENCE-003","SFT-MATH-LOGIC-PROOF-OBJECT-CHECK-004","SFT-MATH-LOGIC-QUANTIFIER-FINITE-SUPPORT-005","SFT-MATH-LOGIC-MODEL-INTERPRETATION-006","SFT-MATH-LOGIC-COMPACTNESS-BOUNDARY-007","SFT-MATH-LOGIC-DECIDABILITY-INTERFACE-008","SFT-MATH-LOGIC-INCOMPLETENESS-SELF-REFERENCE-009","SFT-MATH-LOGIC-FINITE-COLLECTION-010","SFT-MATH-LOGIC-SIZE-BOUNDARY-011","SFT-MATH-LOGIC-CONSTRUCTIVE-CORRESPONDENCE-012","SFT-MATH-LOGIC-MODAL-TEMPORAL-013","SFT-MATH-LOGIC-MANY-VALUED-014","SFT-MATH-LOGIC-NORMALIZATION-015","SFT-MATH-LOGIC-CONSISTENCY-SELF-VERIFICATION-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("LOGIC registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="LOGIC"]
 if len(obs)!=len(IDS)!=16:raise SystemExit("LOGIC census changed")
 p={"schema":"sft-v3-mathematics-logic-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected truth assignment","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
