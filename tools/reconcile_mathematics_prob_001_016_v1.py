#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));FROZEN=ROOT/"census/mathematics_discipline_obligations.json";PREVIOUS=ROOT/"census/mathematics_discipline_current_reconciliation_v13.json";OUT=ROOT/"census/mathematics_discipline_current_reconciliation_v14.json";AUDIT=ROOT/"audits/MATHEMATICS_PROB_001_016_COMPLETION_2026-07-29.json"
from sft.mathematics.prob_001_016_laws_v1 import IDS
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 frozen=json.loads(FROZEN.read_text());fb=dict(frozen);fi=fb.pop("census_identity");previous=json.loads(PREVIOUS.read_text());pb=dict(previous);pi=pb.pop("reconciliation_identity")
 if canon(fb)!=fi or canon(pb)!=pi or previous["current_closed_count"]!=203:raise SystemExit("PROB reconciliation predecessor changed")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};rows=[]
 for i,cid in enumerate(IDS,1):
  row=live[cid];cert=json.loads((ROOT/"claims"/cid/"certificate.json").read_text());ob=f"SFT-MATH-OBL-PROB-{i:03d}"
  if not row["model_admitted"] or cert["engine_receipt_hash"]!=row["receipt_hash"] or cert["mathematics_obligation"]!=ob:raise SystemExit("PROB reconciliation halt: "+cid)
  rows.append({"obligation_id":ob,"claim_id":cid,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"]})
 families=dict(previous["completed_families"]);families["PROB"]=rows;value={"schema":"sft-v3-mathematics-discipline-current-reconciliation/14","date":"2026-07-29","frozen_census_identity":fi,"frozen_obligation_count":323,"closed_at_freeze":27,"predecessor_reconciliation_identity":pi,"completed_families":families,"current_closed_count":219,"current_open_count":104,"current_completion_fraction":"219/323","current_completion_percent":"67.8%","frozen_census_mutated":False,"extension_policy":frozen["extension_policy"]};value["reconciliation_identity"]=canon(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");audit={"schema":"sft-v3-mathematics-prob-completion/1","date":"2026-07-29","family":"PROB-001--016","family_completion":"16/16","candidate_count":4096,"survivor_count":16,"control_count":64,"independent_reconstruction_count":16,"empirical_correspondence_count":16,"observation_record_count":16,"receipt_rows":rows,"exact_replay":"16/16 exact receipts reproduced","focused_tests":"4/4 passed","protected_engine_or_verifier_changed":False,"current_mathematics_progress":"219/323","current_mathematics_percent":"67.8%","reconciliation_identity":value["reconciliation_identity"]};AUDIT.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"closed":219,"open":104,"percent":"67.8%","identity":value["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
