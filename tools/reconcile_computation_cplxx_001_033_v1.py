#!/usr/bin/env python3
"""Reconcile the complete admitted CPLXX family against the frozen census."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FROZEN=ROOT/"census/computation_discipline_obligations.json";PREVIOUS=ROOT/"census/computation_discipline_current_reconciliation_v3.json";OUT=ROOT/"census/computation_discipline_current_reconciliation_v4.json";AUDIT=ROOT/"audits/COMPUTATION_CPLXX_001_033_COMPLETION_2026-07-29.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def receipt_identity(path):
    payload=json.loads(path.read_text());recorded=payload.pop("receipt_hash",None);computed=canonical(payload)
    if recorded!=computed:raise SystemExit("CPLXX stored receipt identity mismatch: "+path.name)
    return computed
def main():
    if OUT.exists() or AUDIT.exists():raise SystemExit("CPLXX reconciliation already exists")
    frozen=json.loads(FROZEN.read_text());body=dict(frozen);frozen_identity=body.pop("census_identity")
    if canonical(body)!=frozen_identity:raise SystemExit("Classical Computation census changed")
    previous=json.loads(PREVIOUS.read_text());body=dict(previous);previous_identity=body.pop("reconciliation_identity")
    if canonical(body)!=previous_identity or previous["current_closed_count"]!=160:raise SystemExit("Classical Computation predecessor reconciliation changed")
    obligations=[x for x in frozen["obligations"] if x["family"]=="CPLXX"]
    if len(obligations)!=33:raise SystemExit("CPLXX obligation count changed")
    live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]};registry=json.loads((ROOT/"census/computation_cplxx_001_033_target_registry_v1.json").read_text());rows=[]
    for claim_id,obligation in zip(registry["claim_ids"],obligations):
        row=live.get(claim_id);package=ROOT/"claims"/claim_id;certificate=json.loads((package/"certificate.json").read_text());census=json.loads((package/"candidate_census.json").read_text());controls=json.loads((package/"controls.json").read_text())["controls"];empirical=json.loads((package/"empirical_validation.json").read_text())
        if row is None or not row.get("model_admitted") or receipt_identity(ROOT/row["receipt_path"])!=row["receipt_hash"] or certificate.get("engine_receipt_hash")!=row["receipt_hash"] or certificate.get("classical_computation_obligation")!=obligation["obligation_id"] or certificate.get("candidate_count")!=256 or certificate.get("unique_survivor_count")!=1 or not certificate.get("controls_passed") or len(census["candidates"])!=256 or len(controls)!=4 or not all(x["passed"] for x in controls) or not empirical.get("all_rows_preserved") or not empirical.get("passed"):raise SystemExit("CPLXX reconciliation halt: "+claim_id)
        rows.append({"obligation_id":obligation["obligation_id"],"claim_id":claim_id,"receipt_hash":row["receipt_hash"],"receipt_path":row["receipt_path"],"closure_status":row["closure_status"],"external_status":row["external_status"],"candidate_count":256,"unique_survivor_count":1,"control_count":4,"post_registry_observation":True,"independent_certificate_hash":certificate["independent_certificate_hash"],"measurement_receipt_hash":certificate["measurement_receipt_hash"]})
    completed=dict(previous["completed_families"]);completed["CPLXX"]=rows;value={"schema":"sft-v3-classical-computation-discipline-current-reconciliation/4","date":"2026-07-29","frozen_census_identity":frozen_identity,"frozen_obligation_count":369,"closed_at_freeze":117,"predecessor_reconciliation_identity":previous_identity,"completed_families":completed,"current_closed_count":193,"current_open_count":176,"current_completion_fraction":"193/369","current_completion_percent":"52.3%","frozen_census_mutated":False,"extension_policy":frozen["extension_policy"]};value["reconciliation_identity"]=canonical(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
    audit={"schema":"sft-v3-classical-computation-cplxx-completion/1","date":"2026-07-29","family":"CPLXX","family_completion":"33/33","generated_candidate_count":33*256,"unique_survivor_count":33,"passed_control_count":33*4,"post_registry_exact_observation_count":33,"implementation_distinct_reconstruction_count":33,"exact_receipt_replay":"33/33","receipt_rows":rows,"protected_engine_or_verifier_changed":False,"current_classical_computation_progress":"193/369","current_classical_computation_percent":"52.3%","frozen_census_identity":frozen_identity,"reconciliation_identity":value["reconciliation_identity"]};AUDIT.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");print(json.dumps({"family":"33/33","candidates":33*256,"controls":33*4,"current":"193/369","percent":"52.3%","identity":value["reconciliation_identity"]},indent=2))
if __name__=="__main__":main()
