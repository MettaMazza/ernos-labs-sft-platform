#!/usr/bin/env python3
"""Freeze NOISE claim identities and questions before observation access."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/information_science_noise_001_012_target_registry_v1.json"
IDS=("SFT-INFO-NOISE-DISTINCTION-CLOSURE-001","SFT-INFO-NOISE-SOURCE-OUTPUT-MISMATCH-002","SFT-INFO-NOISE-PATTERN-SUPPORT-003","SFT-INFO-NOISE-COMPOSITION-004","SFT-INFO-NOISE-DETECTION-005","SFT-INFO-NOISE-LOCALIZATION-006","SFT-INFO-NOISE-ESTIMATION-007","SFT-INFO-NOISE-ERASURE-SUBSTITUTION-008","SFT-INFO-NOISE-BURST-CORRELATION-009","SFT-INFO-NOISE-ADVERSARIAL-SUPPORT-010","SFT-INFO-NOISE-BUDGET-LEDGER-011","SFT-INFO-NOISE-COMPLETENESS-012")
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("NOISE registry already frozen")
 census=json.loads((ROOT/"census/information_science_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="NOISE"]
 if len(rows)!=len(IDS)!=12:raise SystemExit("NOISE census changed")
 p={"schema":"sft-v3-information-science-noise-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"information_science_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected noise result","selected survivor","match result","imported stochastic noise distribution or fitted threshold"]};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
