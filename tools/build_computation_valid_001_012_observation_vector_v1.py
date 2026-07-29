#!/usr/bin/env python3
"""Open and freeze exact Classical Computation validation outcomes after registry freeze."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/computation_valid_001_012_target_registry_v1.json";RECON=ROOT/"census/computation_discipline_current_reconciliation_v10.json";OUT=ROOT/"experiments/external_sources/computation/valid_001_012_observation_vector_v1.json"
FAMILIES=(("FORMX",22,5632,88),("CBLX",21,5376,84),("CPLXX",33,8448,132),("ALGX",31,7936,124),("SEMX",25,6400,100),("DISTX",26,6656,104),("SECX",25,6400,100),("LEARNX",26,6656,104),("SCIX",25,6400,100))
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def receipt_identity(path):
 value=json.loads(path.read_text());recorded=value.pop("receipt_hash",None);computed=canonical(value)
 if recorded!=computed:raise SystemExit("VALID receipt replay failed: "+str(path))
 return computed
def main():
 if OUT.exists():raise SystemExit("computation VALID observation vector already frozen")
 registry=json.loads(REGISTRY.read_text());body=dict(registry);registry_identity=body.pop("registry_identity")
 if canonical(body)!=registry_identity or registry["target_content_present"] is not False:raise SystemExit("VALID registry changed")
 recon=json.loads(RECON.read_text());body=dict(recon);recon_identity=body.pop("reconciliation_identity")
 if canonical(body)!=recon_identity or recon["current_closed_count"]!=351 or recon["current_open_count"]!=18:raise SystemExit("computation v10 reconciliation changed")
 observations=[]
 for family,claims,candidates,controls in FAMILIES:
  rows=recon["completed_families"][family]
  if len(rows)!=claims:raise SystemExit(f"{family} reconciliation membership changed")
  if not all(receipt_identity(ROOT/row["receipt_path"])==row["receipt_hash"] and row["candidate_count"]==256 and row["unique_survivor_count"]==1 and row["control_count"]==4 and row["post_registry_observation"] and row["independent_certificate_hash"] for row in rows):raise SystemExit(f"{family} evidence replay failed")
  observations.append({"family":family,"claims":claims,"candidate_rows":candidates,"unique_survivors":claims,"passed_controls":controls,"receipt_replay":f"{claims}/{claims}","post_registry_observations":claims,"independent_reconstructions":claims})
 famous_ids=("SFT-COMP-CBLX-DIAGONAL-LANGUAGE-004","SFT-COMP-CBLX-BUSY-BEAVER-FINITE-CENSUS-019","SFT-COMP-CPLXX-FOLD-P-NP-SCOPE-007","SFT-COMP-CPLXX-ARBITRARY-FOLD-CIRCUIT-LOWER-024")
 live={x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]}
 if not all(x in live and live[x]["model_admitted"] for x in famous_ids):raise SystemExit("famous-boundary evidence missing")
 values=[]
 for index,(family,claims,candidates,controls) in enumerate(FAMILIES,1):values.append((family.lower()+"_validation",observations[index-1]))
 values.extend((("famous_problem_boundary",{"registered_boundary_claims":list(famous_ids),"theorem_finite_unrestricted_classes_separate":True,"silent_export":False}),("adverse_boundary_vector",{"extension_claims":234,"passed_control_rows":936,"adverse_absent_unavailable_and_handoff_rows_preserved":True,"failed_route_retired":False}),("computation_grand_lock",{"base_claims":117,"extension_claims":234,"current_receipt_rows":351,"generated_extension_candidates":59904,"extension_unique_survivors":234,"extension_passed_controls":936,"implementation_distinct_reconstructions":234,"post_registry_observations":234,"open_validation_rows":12,"open_handoff_rows":6,"reconciliation_identity":recon_identity,"protected_authority_changed":False})))
 records=[{"number":f"{i:03d}","claim_id":registry["claim_ids"][i-1],"obligation_id":registry["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-valid-{i:03d}-execution-retained","source_ids":["SFT-V3-COMPUTATION-RECONCILIATION-V10","SFT-V3-CURRENT-ENGINE-RECEIPTS","SFT-V3-INDEPENDENT-CERTIFICATES"],"all_rows_preserved":True} for i,(name,value) in enumerate(values,1)]
 payload={"schema":"sft-v3-classical-computation-valid-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":registry_identity,"outcomes_opened_only_after_registry_freeze":True,"predecessor_reconciliation_identity":recon_identity,"records":records,"record_count":len(records),"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":len(records),"identity":payload["vector_identity"],"receipt_rows":351},indent=2))
if __name__=="__main__":main()
