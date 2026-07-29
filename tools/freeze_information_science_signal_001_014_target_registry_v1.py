#!/usr/bin/env python3
"""Freeze SIGNAL claim identities and questions before observation access."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/information_science_signal_001_014_target_registry_v1.json"
IDS=("SFT-INFO-SIGNAL-ORDERED-RECORD-001","SFT-INFO-SIGNAL-AMPLITUDE-SUPPORT-002","SFT-INFO-SIGNAL-SAMPLING-SELECTION-003","SFT-INFO-SIGNAL-FINITE-SUFFICIENCY-004","SFT-INFO-SIGNAL-ALIASING-005","SFT-INFO-SIGNAL-QUANTIZATION-PARTITION-006","SFT-INFO-SIGNAL-QUANTIZATION-ERROR-007","SFT-INFO-SIGNAL-RECONSTRUCTION-008","SFT-INFO-SIGNAL-INTERPOLATION-BOUNDARY-009","SFT-INFO-SIGNAL-TRANSFORM-REPRESENTATION-010","SFT-INFO-SIGNAL-TIME-FREQUENCY-011","SFT-INFO-SIGNAL-SPATIAL-MULTIDIMENSIONAL-012","SFT-INFO-SIGNAL-PROVENANCE-013","SFT-INFO-SIGNAL-COMPLETENESS-014")
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("SIGNAL registry already frozen")
 census=json.loads((ROOT/"census/information_science_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="SIGNAL"]
 if len(rows)!=len(IDS)!=14:raise SystemExit("SIGNAL census changed")
 p={"schema":"sft-v3-information-science-signal-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"information_science_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all fourteen claims; no proper subset","prohibited_target_fields":["expected signal result","selected survivor","match result","imported continuum sampling or transform answer"]};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":14,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
