#!/usr/bin/env python3
"""Freeze COMP claim identities and questions before observation access."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/information_science_comp_001_014_target_registry_v1.json"
IDS=("SFT-INFO-COMP-LOSSLESS-RECONSTRUCTION-001","SFT-INFO-COMP-PREFIX-TREE-002","SFT-INFO-COMP-DICTIONARY-003","SFT-INFO-COMP-RUN-RECURRENCE-004","SFT-INFO-COMP-TRANSFORM-005","SFT-INFO-COMP-SOURCE-MODEL-BOUNDARY-006","SFT-INFO-COMP-REDUNDANCY-007","SFT-INFO-COMP-MINIMUM-DESCRIPTION-008","SFT-INFO-COMP-LOSSY-COARSENING-009","SFT-INFO-COMP-DISTORTION-010","SFT-INFO-COMP-RATE-DISTORTION-BOUNDARY-011","SFT-INFO-COMP-SUCCESSIVE-REFINEMENT-012","SFT-INFO-COMP-SIDE-INFORMATION-013","SFT-INFO-COMP-COMPLETENESS-014")
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("COMP registry already frozen")
 census=json.loads((ROOT/"census/information_science_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="COMP"]
 if len(rows)!=len(IDS)!=14:raise SystemExit("COMP census changed")
 p={"schema":"sft-v3-information-science-comp-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"information_science_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all fourteen claims; no proper subset","prohibited_target_fields":["expected compression result","selected survivor","match result","imported entropy or rate-distortion answer"]};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":14,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
