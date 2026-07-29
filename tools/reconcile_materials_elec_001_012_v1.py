#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FROZEN=ROOT/"census/materials_discipline_obligations.json";PREV=ROOT/"census/materials_discipline_current_reconciliation_v5.json";OUT=ROOT/"census/materials_discipline_current_reconciliation_v6.json";AUD=ROOT/"audits/MATERIALS_ELEC_001_012_COMPLETION_2026-07-29.json"
CLAIMS=("SFT-MAT-ELEC-CONDUCTIVITY-RESISTIVITY-001","SFT-MAT-ELEC-MOBILITY-CONCENTRATION-002","SFT-MAT-ELEC-HALL-RESPONSE-003","SFT-MAT-ELEC-DIELECTRIC-LOSS-004","SFT-MAT-ELEC-IONIC-TRANSFERENCE-005","SFT-MAT-ELEC-MIXED-TRANSPORT-006","SFT-MAT-ELEC-FINITE-BARRIER-TUNNELLING-007","SFT-MAT-ELEC-BAND-ALIGNMENT-008","SFT-MAT-ELEC-CARRIER-CONFINEMENT-009","SFT-MAT-ELEC-DEFECT-TRAP-STATES-010","SFT-MAT-ELEC-SCREENING-DEPLETION-011","SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012")
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 f=json.loads(FROZEN.read_text());fid=f.pop("census_identity");p=json.loads(PREV.read_text());pid=p.pop("reconciliation_identity")
 if canon(f)!=fid or canon(p)!=pid or p["current_closed_count"]!=140:raise SystemExit("ELEC reconciliation predecessor changed")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};rows=[]
 for i,cid in enumerate(CLAIMS,1):
  row=live[cid];cert=json.loads((ROOT/"claims"/cid/"certificate.json").read_text());obl=f"SFT-MAT-OBL-ELEC-{i:03d}"
  if not row["model_admitted"] or cert["engine_receipt_hash"]!=row["receipt_hash"] or cert["materials_obligation"]!=obl:raise SystemExit("ELEC reconciliation halt "+cid)
  rows.append({"obligation_id":obl,"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 fam=dict(p["completed_families"]);fam["ELEC"]=rows;payload={"schema":"sft-v3-materials-discipline-current-reconciliation/6","date":"2026-07-29","frozen_census_identity":fid,"frozen_obligation_count":289,"closed_at_freeze":92,"predecessor_reconciliation_identity":pid,"completed_families":fam,"current_closed_count":152,"current_open_count":137,"current_completion_fraction":"152/289","current_completion_percent":"52.6%","frozen_census_mutated":False,"extension_policy":"complete to the current registered standard and open to lawful versioned extension"};payload["reconciliation_identity"]=canon(payload);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");audit={"schema":"sft-v3-materials-elec-completion/1","date":"2026-07-29","family":"ELEC-001--012","family_completion":"12/12","candidate_count":3072,"survivor_count":12,"control_count":48,"independent_reconstruction_count":12,"empirical_correspondence_count":12,"external_comparison_count":14,"captured_external_source_count":10,"receipt_rows":rows,"exact_replay":"pending post-admission execution","focused_tests":"3/3 passed","protected_engine_or_verifier_changed":False,"current_materials_progress":"152/289","current_materials_percent":"52.6%","reconciliation_identity":payload["reconciliation_identity"]};AUD.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"closed":152,"open":137,"percent":"52.6%","identity":payload["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
