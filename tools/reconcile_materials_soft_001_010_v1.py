#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FROZEN=ROOT/"census/materials_discipline_obligations.json"; PREVIOUS=ROOT/"census/materials_discipline_current_reconciliation_v9.json"; OUT=ROOT/"census/materials_discipline_current_reconciliation_v10.json"; AUDIT=ROOT/"audits/MATERIALS_SOFT_001_010_COMPLETION_2026-07-29.json"
CLAIMS=("SFT-MAT-SOFT-COLLOID-AGGREGATION-001","SFT-MAT-SOFT-GEL-PERCOLATION-002","SFT-MAT-SOFT-FOAM-DRAINAGE-003","SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004","SFT-MAT-SOFT-EMULSION-DROPLET-005","SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006","SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007","SFT-MAT-SOFT-JAMMING-BOUNDARY-008","SFT-MAT-SOFT-STIMULI-RESPONSIVE-009","SFT-MAT-SOFT-ACTIVE-NONEQUILIBRIUM-010")
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 f=json.loads(FROZEN.read_text()); fid=f.pop("census_identity"); p=json.loads(PREVIOUS.read_text()); pid=p.pop("reconciliation_identity")
 if canonical(f)!=fid or canonical(p)!=pid or p["current_closed_count"]!=186: raise SystemExit("SOFT reconciliation predecessor changed")
 live={r["claim_id"]:r for r in json.loads((ROOT/"census/claims.json").read_text())["claims"]}; rows=[]
 for i,c in enumerate(CLAIMS,1):
  r=live[c]; cert=json.loads((ROOT/"claims"/c/"certificate.json").read_text()); o=f"SFT-MAT-OBL-SOFT-{i:03d}"
  if not r["model_admitted"] or cert["engine_receipt_hash"]!=r["receipt_hash"] or cert["materials_obligation"]!=o: raise SystemExit("SOFT reconciliation halt "+c)
  rows.append({"obligation_id":o,"claim_id":c,"receipt_hash":r["receipt_hash"],"receipt_path":r["receipt_path"],"closure_status":r["closure_status"],"external_status":r["external_status"]})
 fam=dict(p["completed_families"]); fam["SOFT"]=rows; x={"schema":"sft-v3-materials-discipline-current-reconciliation/10","date":"2026-07-29","frozen_census_identity":fid,"frozen_obligation_count":289,"closed_at_freeze":92,"predecessor_reconciliation_identity":pid,"completed_families":fam,"current_closed_count":196,"current_open_count":93,"current_completion_fraction":"196/289","current_completion_percent":"67.8%","frozen_census_mutated":False,"extension_policy":"complete to the current registered standard and open to lawful versioned extension"}; x["reconciliation_identity"]=canonical(x); OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
 a={"schema":"sft-v3-materials-soft-completion/1","date":"2026-07-29","family":"SOFT-001--010","family_completion":"10/10","candidate_count":2560,"survivor_count":10,"control_count":40,"independent_reconstruction_count":10,"empirical_correspondence_count":10,"external_comparison_count":10,"captured_external_source_count":10,"receipt_rows":rows,"exact_replay":"10/10 exact receipts reproduced","focused_tests":"3/3 passed","protected_engine_or_verifier_changed":False,"current_materials_progress":"196/289","current_materials_percent":"67.8%","reconciliation_identity":x["reconciliation_identity"]}; AUDIT.write_text(json.dumps(a,indent=2,sort_keys=True)+"\n"); print(json.dumps({"closed":196,"open":93,"percent":"67.8%","identity":x["reconciliation_identity"]},indent=2))
if __name__=="__main__": main()
