#!/usr/bin/env python3
"""Admit and materialize the eight Materials successor claims sequentially."""
from __future__ import annotations
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.engine import EngineRepository
from sft.materials.successor_evidence import PRE_SOURCE_SEAL_PATH,SPECS
def write(path,payload): path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load(cid):
 p=ROOT/"claims"/cid/"execution.py"; d=importlib.util.spec_from_file_location("mat2_"+cid.replace("-","_"),p); m=importlib.util.module_from_spec(d); d.loader.exec_module(m); return m.build_execution(ROOT)
def manifest(cid):
 p=ROOT/"census/execution_manifest.json"; x=json.loads(p.read_text());
 if cid not in {r["claim_id"] for r in x["claims"]}: x["claims"].append({"claim_id":cid,"execution_file":f"claims/{cid}/execution.py"}); write(p,x)
def main():
 repo=EngineRepository(ROOT)
 for i,spec in enumerate(SPECS,1):
  execution=load(spec.claim_id); captured={}
  class I:
   def validate(self,sealed): captured["sealed"]=sealed; captured["external"]=execution.independent_validator.validate(sealed); return captured["external"]
  class E:
   def validate(self,sealed): captured["empirical"]=execution.empirical_validator.validate(sealed); return captured["empirical"]
  receipt=repo.execute_official(execution.program,I(),execution.source_files,E()); manifest(spec.claim_id)
  census=json.loads((ROOT/"census/claims.json").read_text()); row=next(x for x in census["claims"] if x["claim_id"]==spec.claim_id); sealed=captured["sealed"]; empirical=captured["empirical"]; package=ROOT/"claims"/spec.claim_id
  write(package/"candidate_census.json",{"claim_id":spec.claim_id,**asdict(sealed.census)}); write(package/"elimination_receipt.json",{"claim_id":spec.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)}); write(package/"controls.json",{"claim_id":spec.claim_id,"controls":asdict(sealed)["controls"]}); write(package/"empirical_validation.json",{"claim_id":spec.claim_id,**asdict(empirical)})
  cert={"claim_id":spec.claim_id,"status":"model_admitted_authoritatively_corresponded_and_independently_replicated","pre_source_complete_successor_seal":PRE_SOURCE_SEAL_PATH,"derivation_seal_hash":sealed.seal_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"external_data_source_ids":list(empirical.data_source_ids),"all_external_rows_preserved":empirical.all_rows_preserved,"specimen_dependent_magnitude_claimed_as_universal":False}
  write(package/"certificate.json",cert); reg=json.loads((package/"registration.json").read_text()); reg["status"]="empirically_tested"; write(package/"registration.json",reg); (package/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_authoritatively_corresponded_and_independently_replicated`\n\n- Engine receipt: `{receipt.receipt_hash}`\n- Derivation seal: `{sealed.seal_hash}`\n",encoding="utf-8")
  print(f"[{i}/8] {spec.claim_id} {receipt.receipt_hash}")
if __name__=="__main__": main()
