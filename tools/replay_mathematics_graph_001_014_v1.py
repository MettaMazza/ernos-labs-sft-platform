#!/usr/bin/env python3
"""Exact read-only replay of all fourteen admitted GRAPH receipts."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sft.engine import AuthorityLedger,SFTAdmissionEngine
from sft.engine.receipt_io import read_receipt
from sft.engine.source import build_source_manifest
from sft.mathematics.graph_001_014_laws_v1 import IDS as ORDER
from sft.verification import _load_execution,_sealed_replay_environment
def main():
 census=json.loads((ROOT/"census/claims.json").read_text())["claims"];manifest=json.loads((ROOT/"census/execution_manifest.json").read_text())["claims"]
 if [x["claim_id"] for x in census]!=[x["claim_id"] for x in manifest]:raise SystemExit("GRAPH replay halted: census and manifest differ")
 indices={x["claim_id"]:i for i,x in enumerate(census)};first=min(indices[x] for x in ORDER);authority=AuthorityLedger()
 for row in census[:first]:authority.admit(read_receipt(ROOT/row["receipt_path"]))
 engine=SFTAdmissionEngine(authority);results=[]
 for cid in ORDER:
  i=indices[cid];row=census[i];execution=_load_execution(ROOT,manifest[i])
  with _sealed_replay_environment(ROOT,cid,execution.empirical_validator):receipt=engine.run(execution.program,execution.independent_validator,execution.empirical_validator,executed_source_hash=build_source_manifest(ROOT,execution.source_files).manifest_hash)
  stored=read_receipt(ROOT/row["receipt_path"])
  if receipt!=stored or receipt.receipt_hash!=row["receipt_hash"]:raise SystemExit("GRAPH exact replay mismatch: "+cid)
  authority.admit(receipt);results.append(cid);print(f"[{len(results)}/{len(ORDER)}] exact replay {cid}: {receipt.receipt_hash}",flush=True)
 print(json.dumps({"replayed":len(results),"all_exact":True},indent=2))
if __name__=="__main__":main()
