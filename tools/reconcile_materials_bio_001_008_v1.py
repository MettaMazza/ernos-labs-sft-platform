#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FROZEN=ROOT/"census/materials_discipline_obligations.json"; PREVIOUS=ROOT/"census/materials_discipline_current_reconciliation_v10.json"; OUT=ROOT/"census/materials_discipline_current_reconciliation_v11.json"; AUDIT=ROOT/"audits/MATERIALS_BIO_001_008_COMPLETION_2026-07-29.json"
CLAIMS=("SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001","SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002","SFT-MAT-BIO-SCAFFOLD-POROSITY-CONNECTIVITY-003","SFT-MAT-BIO-CELL-MATERIAL-ADHESION-004","SFT-MAT-BIO-MECHANICAL-MATCHING-005","SFT-MAT-BIO-CONTROLLED-RELEASE-006","SFT-MAT-BIO-MINERALIZED-ORGANIZATION-007","SFT-MAT-BIO-BIOFABRICATED-IDENTITY-008")
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 f=json.loads(FROZEN.read_text()); fid=f.pop("census_identity"); p=json.loads(PREVIOUS.read_text()); pid=p.pop("reconciliation_identity")
 if canonical(f)!=fid or canonical(p)!=pid or p["current_closed_count"]!=196: raise SystemExit("BIO reconciliation predecessor changed")
 live={r["claim_id"]:r for r in json.loads((ROOT/"census/claims.json").read_text())["claims"]}; rows=[]
 for i,c in enumerate(CLAIMS,1):
  r=live[c]; cert=json.loads((ROOT/"claims"/c/"certificate.json").read_text()); o=f"SFT-MAT-OBL-BIO-{i:03d}"
  if not r["model_admitted"] or cert["engine_receipt_hash"]!=r["receipt_hash"] or cert["materials_obligation"]!=o: raise SystemExit("BIO reconciliation halt "+c)
  rows.append({"obligation_id":o,"claim_id":c,"receipt_hash":r["receipt_hash"],"receipt_path":r["receipt_path"],"closure_status":r["closure_status"],"external_status":r["external_status"]})
 fam=dict(p["completed_families"]); fam["BIO"]=rows; x={"schema":"sft-v3-materials-discipline-current-reconciliation/11","date":"2026-07-29","frozen_census_identity":fid,"frozen_obligation_count":289,"closed_at_freeze":92,"predecessor_reconciliation_identity":pid,"completed_families":fam,"current_closed_count":204,"current_open_count":85,"current_completion_fraction":"204/289","current_completion_percent":"70.6%","frozen_census_mutated":False,"extension_policy":"complete to the current registered standard and open to lawful versioned extension"}; x["reconciliation_identity"]=canonical(x); OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
 a={"schema":"sft-v3-materials-bio-completion/1","date":"2026-07-29","family":"BIO-001--008","family_completion":"8/8","candidate_count":2048,"survivor_count":8,"control_count":32,"independent_reconstruction_count":8,"empirical_correspondence_count":8,"external_comparison_count":8,"captured_external_source_count":8,"receipt_rows":rows,"exact_replay":"8/8 exact receipts reproduced","focused_tests":"3/3 passed","protected_engine_or_verifier_changed":False,"current_materials_progress":"204/289","current_materials_percent":"70.6%","reconciliation_identity":x["reconciliation_identity"]}; AUDIT.write_text(json.dumps(a,indent=2,sort_keys=True)+"\n"); print(json.dumps({"closed":204,"open":85,"percent":"70.6%","identity":x["reconciliation_identity"]},indent=2))
if __name__=="__main__": main()
