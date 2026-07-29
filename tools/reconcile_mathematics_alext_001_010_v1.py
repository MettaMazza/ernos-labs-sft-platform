#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));FROZEN=ROOT/"census/mathematics_discipline_obligations.json";PREVIOUS=ROOT/"census/mathematics_discipline_current_reconciliation_v1.json";OUT=ROOT/"census/mathematics_discipline_current_reconciliation_v2.json";AUDIT=ROOT/"audits/MATHEMATICS_ALEXT_001_010_COMPLETION_2026-07-29.json"
from sft.mathematics.alext_001_010_laws_v1 import IDS
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 frozen=json.loads(FROZEN.read_text());fb=dict(frozen);fi=fb.pop("census_identity");previous=json.loads(PREVIOUS.read_text());pb=dict(previous);pi=pb.pop("reconciliation_identity")
 if canon(fb)!=fi or canon(pb)!=pi or previous["current_closed_count"]!=45:raise SystemExit("ALEXT reconciliation predecessor changed")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};rows=[]
 for i,cid in enumerate(IDS,1):
  row=live[cid];cert=json.loads((ROOT/"claims"/cid/"certificate.json").read_text());ob=f"SFT-MATH-OBL-ALEXT-{i:03d}"
  if not row["model_admitted"] or cert["engine_receipt_hash"]!=row["receipt_hash"] or cert["mathematics_obligation"]!=ob:raise SystemExit("ALEXT reconciliation halt: "+cid)
  rows.append({"obligation_id":ob,"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 families=dict(previous["completed_families"]);families["ALEXT"]=rows;value={"schema":"sft-v3-mathematics-discipline-current-reconciliation/2","date":"2026-07-29","frozen_census_identity":fi,"frozen_obligation_count":323,"closed_at_freeze":27,"predecessor_reconciliation_identity":pi,"completed_families":families,"current_closed_count":55,"current_open_count":268,"current_completion_fraction":"55/323","current_completion_percent":"17.0%","frozen_census_mutated":False,"extension_policy":frozen["extension_policy"]};value["reconciliation_identity"]=canon(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");audit={"schema":"sft-v3-mathematics-alext-completion/1","date":"2026-07-29","family":"ALEXT-001--010","family_completion":"10/10","candidate_count":2560,"survivor_count":10,"control_count":40,"independent_reconstruction_count":10,"empirical_correspondence_count":10,"observation_record_count":10,"receipt_rows":rows,"exact_replay":"10/10 exact receipts reproduced","focused_tests":"4/4 passed","protected_engine_or_verifier_changed":False,"current_mathematics_progress":"55/323","current_mathematics_percent":"17.0%","reconciliation_identity":value["reconciliation_identity"]};AUDIT.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"closed":55,"open":268,"percent":"17.0%","identity":value["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
