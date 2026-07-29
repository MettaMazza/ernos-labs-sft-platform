#!/usr/bin/env python3
"""Freeze CHAN claim identities and questions before observation access."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/information_science_chan_001_018_target_registry_v1.json"
IDS=("SFT-INFO-CHAN-INPUT-OUTPUT-RELATION-001","SFT-INFO-CHAN-DETERMINISTIC-TRANSPORT-002","SFT-INFO-CHAN-OBSERVATION-EQUIVALENCE-003","SFT-INFO-CHAN-SINGLE-USER-CAPACITY-004","SFT-INFO-CHAN-RESOURCE-CAPACITY-005","SFT-INFO-CHAN-NOISELESS-COMPOSITION-006","SFT-INFO-CHAN-CASCADE-BOUNDARY-007","SFT-INFO-CHAN-PARALLEL-COMPOSITION-008","SFT-INFO-CHAN-FEEDBACK-009","SFT-INFO-CHAN-MULTIPLE-ACCESS-010","SFT-INFO-CHAN-BROADCAST-011","SFT-INFO-CHAN-RELAY-012","SFT-INFO-CHAN-INTERFERENCE-013","SFT-INFO-CHAN-BIDIRECTIONAL-014","SFT-INFO-CHAN-NETWORK-CUT-015","SFT-INFO-CHAN-FINITE-USE-SUCCESSION-016","SFT-INFO-CHAN-SIMULATION-017","SFT-INFO-CHAN-COMPLETENESS-018")
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("CHAN registry already frozen")
 census=json.loads((ROOT/"census/information_science_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="CHAN"]
 if len(rows)!=len(IDS)!=18:raise SystemExit("CHAN census changed")
 p={"schema":"sft-v3-information-science-chan-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"information_science_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all eighteen claims; no proper subset","prohibited_target_fields":["expected capacity result","selected survivor","match result","imported Shannon formula or stochastic channel answer"]};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":18,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
