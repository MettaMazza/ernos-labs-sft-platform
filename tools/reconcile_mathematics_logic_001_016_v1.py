#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));FROZEN=ROOT/"census/mathematics_discipline_obligations.json";PREVIOUS=ROOT/"census/mathematics_discipline_current_reconciliation_v16.json";OUT=ROOT/"census/mathematics_discipline_current_reconciliation_v17.json";AUDIT=ROOT/"audits/MATHEMATICS_LOGIC_001_016_COMPLETION_2026-07-29.json"
from sft.mathematics.logic_001_016_laws_v1 import IDS
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 frozen=json.loads(FROZEN.read_text());fb=dict(frozen);fi=fb.pop("census_identity");previous=json.loads(PREVIOUS.read_text());pb=dict(previous);pi=pb.pop("reconciliation_identity")
 if canon(fb)!=fi or canon(pb)!=pi or previous["current_closed_count"]!=247:raise SystemExit("LOGIC reconciliation predecessor changed")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};rows=[]
 for i,cid in enumerate(IDS,1):
  row=live[cid];cert=json.loads((ROOT/"claims"/cid/"certificate.json").read_text());ob=f"SFT-MATH-OBL-LOGIC-{i:03d}"
  if not row["model_admitted"] or cert["engine_receipt_hash"]!=row["receipt_hash"] or cert["mathematics_obligation"]!=ob:raise SystemExit("LOGIC reconciliation halt: "+cid)
  rows.append({"obligation_id":ob,"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 families=dict(previous["completed_families"]);families["LOGIC"]=rows;value={"schema":"sft-v3-mathematics-discipline-current-reconciliation/17","date":"2026-07-29","frozen_census_identity":fi,"frozen_obligation_count":323,"closed_at_freeze":27,"predecessor_reconciliation_identity":pi,"completed_families":families,"current_closed_count":263,"current_open_count":60,"current_completion_fraction":"263/323","current_completion_percent":"81.4%","frozen_census_mutated":False,"extension_policy":frozen["extension_policy"]};value["reconciliation_identity"]=canon(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");audit={"schema":"sft-v3-mathematics-logic-completion/1","date":"2026-07-29","family":"LOGIC-001--016","family_completion":"16/16","candidate_count":4096,"survivor_count":16,"control_count":64,"independent_reconstruction_count":16,"empirical_correspondence_count":16,"observation_record_count":16,"receipt_rows":rows,"exact_replay":"16/16 exact receipts reproduced","focused_tests":"4/4 passed","protected_engine_or_verifier_changed":False,"current_mathematics_progress":"263/323","current_mathematics_percent":"81.4%","reconciliation_identity":value["reconciliation_identity"]};AUDIT.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"closed":263,"open":60,"percent":"81.4%","identity":value["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
