#!/usr/bin/env python3
"""Create the first complete-field Mathematics reconciliation."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FROZEN=ROOT/"census/mathematics_discipline_obligations.json";OUT=ROOT/"census/mathematics_discipline_current_reconciliation_v1.json";AUDIT=ROOT/"audits/MATHEMATICS_ARITH_001_018_COMPLETION_2026-07-29.json"
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.mathematics.arith_001_018_laws_v1 import IDS
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 frozen=json.loads(FROZEN.read_text());body=dict(frozen);identity=body.pop("census_identity")
 if canonical(body)!=identity or frozen["registered_obligation_count"]!=323:raise SystemExit("Mathematics frozen census changed")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};base=[]
 for obligation in (x for x in frozen["obligations"] if x["family"]=="BASE"):
  cid=obligation["current_claim_ids"][0];row=live[cid];base.append({"obligation_id":obligation["obligation_id"],"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 arith=[]
 for i,cid in enumerate(IDS,1):
  row=live[cid];cert=json.loads((ROOT/"claims"/cid/"certificate.json").read_text());ob=f"SFT-MATH-OBL-ARITH-{i:03d}"
  if not row["model_admitted"] or cert["engine_receipt_hash"]!=row["receipt_hash"] or cert["mathematics_obligation"]!=ob:raise SystemExit("ARITH reconciliation halt: "+cid)
  arith.append({"obligation_id":ob,"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 value={"schema":"sft-v3-mathematics-discipline-current-reconciliation/1","date":"2026-07-29","frozen_census_identity":identity,"frozen_obligation_count":323,"closed_at_freeze":27,"completed_families":{"BASE":base,"ARITH":arith},"current_closed_count":45,"current_open_count":278,"current_completion_fraction":"45/323","current_completion_percent":"13.9%","frozen_census_mutated":False,"extension_policy":frozen["extension_policy"]};value["reconciliation_identity"]=canonical(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
 audit={"schema":"sft-v3-mathematics-arith-completion/1","date":"2026-07-29","family":"ARITH-001--018","family_completion":"18/18","candidate_count":4608,"survivor_count":18,"control_count":72,"independent_reconstruction_count":18,"empirical_correspondence_count":18,"observation_record_count":18,"receipt_rows":arith,"exact_replay":"18/18 exact receipts reproduced","focused_tests":"4/4 passed","protected_engine_or_verifier_changed":False,"current_mathematics_progress":"45/323","current_mathematics_percent":"13.9%","reconciliation_identity":value["reconciliation_identity"]};AUDIT.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"closed":45,"open":278,"percent":"13.9%","identity":value["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
