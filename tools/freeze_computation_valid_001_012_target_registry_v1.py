#!/usr/bin/env python3
"""Freeze computation VALID identities before opening reconciliation outcomes."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.computation.valid_001_012_laws_v1 import IDS
OUT=ROOT/"census/computation_valid_001_012_target_registry_v1.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("computation VALID registry already frozen")
 census=json.loads((ROOT/"census/computation_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="VALID"]
 if len(rows)!=len(IDS) or len(IDS)!=12:raise SystemExit("computation VALID census changed")
 payload={"schema":"sft-v3-classical-computation-valid-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"classical_computation_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all twelve validation claims; no proper subset","prohibited_target_fields":["receipt outcome","pass count","selected survivor","grand-lock result"]};payload["registry_identity"]=canonical(payload);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":len(IDS),"identity":payload["registry_identity"]},indent=2))
if __name__=="__main__":main()
