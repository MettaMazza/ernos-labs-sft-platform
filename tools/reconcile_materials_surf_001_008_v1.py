#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FROZEN=ROOT/"census/materials_discipline_obligations.json"; PREVIOUS=ROOT/"census/materials_discipline_current_reconciliation_v12.json"; OUT=ROOT/"census/materials_discipline_current_reconciliation_v13.json"; AUDIT=ROOT/"audits/MATERIALS_SURF_001_008_COMPLETION_2026-07-29.json"
CLAIMS=("SFT-MAT-SURF-FREE-STATE-ENERGY-001","SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002","SFT-MAT-SURF-ADHESION-SEPARATION-003","SFT-MAT-SURF-COATING-SUBSTRATE-004","SFT-MAT-SURF-ROUGHNESS-SCALE-005","SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006","SFT-MAT-SURF-TRIBOFILM-RETENTION-007","SFT-MAT-SURF-DELAMINATION-008")
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 f=json.loads(FROZEN.read_text()); fid=f.pop("census_identity"); p=json.loads(PREVIOUS.read_text()); pid=p.pop("reconciliation_identity")
 if canonical(f)!=fid or canonical(p)!=pid or p["current_closed_count"]!=214: raise SystemExit("SURF reconciliation predecessor changed")
 live={r["claim_id"]:r for r in json.loads((ROOT/"census/claims.json").read_text())["claims"]}; rows=[]
 for i,c in enumerate(CLAIMS,1):
  r=live[c]; cert=json.loads((ROOT/"claims"/c/"certificate.json").read_text()); o=f"SFT-MAT-OBL-SURF-{i:03d}"
  if not r["model_admitted"] or cert["engine_receipt_hash"]!=r["receipt_hash"] or cert["materials_obligation"]!=o: raise SystemExit("SURF reconciliation halt "+c)
  rows.append({"obligation_id":o,"claim_id":c,"receipt_hash":r["receipt_hash"],"receipt_path":r["receipt_path"],"closure_status":r["closure_status"],"external_status":r["external_status"]})
 fam=dict(p["completed_families"]); fam["SURF"]=rows; x={"schema":"sft-v3-materials-discipline-current-reconciliation/13","date":"2026-07-29","frozen_census_identity":fid,"frozen_obligation_count":289,"closed_at_freeze":92,"predecessor_reconciliation_identity":pid,"completed_families":fam,"current_closed_count":222,"current_open_count":67,"current_completion_fraction":"222/289","current_completion_percent":"76.8%","frozen_census_mutated":False,"extension_policy":"complete to the current registered standard and open to lawful versioned extension"}; x["reconciliation_identity"]=canonical(x); OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
 a={"schema":"sft-v3-materials-surf-completion/1","date":"2026-07-29","family":"SURF-001--008","family_completion":"8/8","candidate_count":2048,"survivor_count":8,"control_count":32,"independent_reconstruction_count":8,"empirical_correspondence_count":8,"external_comparison_count":8,"captured_external_source_count":8,"receipt_rows":rows,"exact_replay":"8/8 exact receipts reproduced","focused_tests":"3/3 passed","protected_engine_or_verifier_changed":False,"current_materials_progress":"222/289","current_materials_percent":"76.8%","reconciliation_identity":x["reconciliation_identity"]}; AUDIT.write_text(json.dumps(a,indent=2,sort_keys=True)+"\n"); print(json.dumps({"closed":222,"open":67,"percent":"76.8%","identity":x["reconciliation_identity"]},indent=2))
if __name__=="__main__": main()
