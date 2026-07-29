#!/usr/bin/env python3
"""Freeze ALGX claim identities and questions before observation access."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.computation.algx_001_031_laws_v1 import IDS
OUT=ROOT/"census/computation_algx_001_031_target_registry_v1.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ALGX target registry already frozen")
 census=json.loads((ROOT/"census/computation_discipline_obligations.json").read_text());rows=[x for x in census["obligations"] if x["family"]=="ALGX"]
 if len(rows)!=len(IDS) or len(IDS)!=31:raise SystemExit("ALGX census changed")
 payload={"schema":"sft-v3-classical-computation-algx-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"classical_computation_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in rows],"question_titles":[x["title"] for x in rows],"completion_unit":"all thirty-one claims; no proper subset","prohibited_target_fields":["expected algorithm result","selected survivor","match result","imported library or theorem answer"]};payload["registry_identity"]=canonical(payload);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":len(IDS),"identity":payload["registry_identity"]},indent=2))
if __name__=="__main__":main()
