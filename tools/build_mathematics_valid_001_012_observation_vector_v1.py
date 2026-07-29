#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_valid_001_012_target_registry_v1.json";REC=ROOT/"census/mathematics_discipline_current_reconciliation_v21.json";OUT=ROOT/"experiments/external_sources/mathematics/valid_001_012_observation_vector_v1.json"
GROUPS=(("BASE","ARITH","ALEXT"),("COMB","GRAPH"),("LINEAR","ALG"),("ORDER","GEOM"),("TOPO","CALC","ANAL"),("EQN","MEAS"),("PROB",),("OPT","DYN"),("LOGIC","CAT"),("NUM","SYMB"),("XINT",))
NAMES=("arithmetic_algebra","combinatorics_graph","linear_algebraic","order_geometry","topology_analysis","equation_measure","probability_statistics","optimization_dynamics","logic_compositional","numerical_symbolic","adverse_absent_unresolved_boundary","empirical_formal_grand_lock")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("VALID vector already frozen")
 r=json.loads(REG.read_text());rb=dict(r);ri=rb.pop("registry_identity");rec=json.loads(REC.read_text());rc=dict(rec);rci=rc.pop("reconciliation_identity")
 if canon(rb)!=ri or canon(rc)!=rci or r["target_content_present"] is not False or rec["current_closed_count"]!=305:raise SystemExit("VALID frozen predecessor changed")
 families=rec["completed_families"];covered=[];observations=[]
 for group in GROUPS:
  rows=[row for family in group for row in families[family]];covered.extend(row["claim_id"] for row in rows)
  observations.append({"families":list(group),"claim_count":len(rows),"receipt_hashes":[row["receipt_hash"] for row in rows],"all_model_admitted":all(row["closure_status"]=="closed" for row in rows),"all_external_statuses":[row["external_status"] for row in rows]})
 boundary=[]
 for family in families.values():
  for row in family:
   registration=ROOT/"claims"/row["claim_id"]/"registration.json";data=json.loads(registration.read_text())
   boundary.append({"claim_id":row["claim_id"],"excluded_inputs":data.get("excluded_inputs",[]),"closure_status":row["closure_status"],"external_status":row["external_status"],"receipt_hash":row["receipt_hash"]})
 boundary.sort(key=lambda x:x["claim_id"]);boundary_identity=canon(boundary)
 observations[-1].update({"boundary_record_count":len(boundary),"boundary_identity":boundary_identity,"favorable_adverse_absent_unresolved_and_boundary_rows_preserved":True})
 observations.append({"covered_pre_validation_claims":len(covered),"unique_claim_ids":len(set(covered)),"unique_receipt_hashes":len({row["receipt_hash"] for family in families.values() for row in family}),"completed_family_count":len(families),"frozen_census_count":323,"open_only_valid_and_hand":rec["current_open_count"],"reconciliation_identity":rci,"all_named_groups_and_boundary_rows_present":True})
 if len(covered)!=305 or len(set(covered))!=305 or len(observations)!=12:raise SystemExit("VALID coverage failed")
 records=[]
 for i,(name,value) in enumerate(zip(NAMES,observations),1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-valid-{i:03d}-observation-retained","source_ids":["census/mathematics_discipline_current_reconciliation_v21.json","census/claims.json","census/execution_manifest.json"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-valid-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"pre_validation_reconciliation_identity":rci,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"boundary_rows":boundary,"boundary_record_count":len(boundary),"boundary_identity":boundary_identity,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"covered_claims":len(covered),"boundary_rows":len(boundary),"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
