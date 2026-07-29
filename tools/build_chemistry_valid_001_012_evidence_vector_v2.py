#!/usr/bin/env python3
"""Freeze the factual 263-claim pre-VALID Chemistry evidence surface.

Version two preserves the original 254-count halt and adds the later Smithium
return family plus the formal operational classical/quantum correspondence.
It does not invent empirical records for formal-only claims: those rows retain
their explicit absence and, where applicable, name the separately admitted
family-level empirical comparison.
"""
import hashlib,json
from pathlib import Path
from build_chemistry_valid_001_012_evidence_vector_v1 import ROOT,REPAIR_AUDIT,canonical_digest,digest,obligation_from_certificate,read,vector_memberships

OUTPUT=ROOT/"experiments/external_sources/chemistry/valid_001_012_complete_empirical_vector_v2.json"
EXPECTED=263
FORMAL_SCOPE={
 "SFT-CHEM-OPERATIONAL-CLASSICAL-QUANTUM-CORRESPONDENCE-015":("SFT-CHEM-PRIOR-CQ-015",("011","012"),None,"formal operational correspondence; no apparatus target is selected"),
 "SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001":("SFT-CHEM-RETURN-SMITHIUM",("007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing synthesis grammar"),
 "SFT-CHEM-SMITHIUM-DECAY-CHANNEL-LEDGER-001":("SFT-CHEM-RETURN-SMITHIUM",("007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing decay grammar"),
 "SFT-CHEM-SMITHIUM-LIFETIME-BOUNDARY-001":("SFT-CHEM-RETURN-SMITHIUM",("007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","unmeasured lifetime mandatory halt"),
 "SFT-CHEM-SMITHIUM-ION-OXIDATION-LADDER-001":("SFT-CHEM-RETURN-SMITHIUM",("007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing ion and oxidation ladder"),
 "SFT-CHEM-SMITHIUM-SPECTROSCOPIC-CLASSES-001":("SFT-CHEM-RETURN-SMITHIUM",("005","007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing spectroscopy classes without invented lines"),
 "SFT-CHEM-SMITHIUM-CHEMICAL-SEPARATION-001":("SFT-CHEM-RETURN-SMITHIUM",("007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing chemical-state separation boundary"),
 "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001":("SFT-CHEM-RETURN-SMITHIUM",("005","007","011","012"),"SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001","standing joint-identification protocol"),
}
SUPPLEMENTAL_EMPIRICAL_SCOPE={
 "SFT-CHEM-ROVIBRONIC-COMPOSITION-001":("SFT-CHEM-OBL-FOUND-001",None),
 "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001":("SFT-CHEM-OBL-RETURN-001",("005","007","011","012")),
}

def current_certificate(package:Path,receipt_hash:str)->Path:
 matches=[]
 for path in sorted(package.glob("certificate*.json")):
  if read(path).get("engine_receipt_hash")==receipt_hash:matches.append(path)
 if len(matches)!=1:raise SystemExit(f"{package.name} requires exactly one current certificate, found {len(matches)}")
 return matches[0]

def main():
 if OUTPUT.exists():raise SystemExit("v2 Chemistry VALID vector already exists; freeze preserved")
 census=read(ROOT/"census/claims.json");rows=sorted((r for r in census["claims"] if r.get("branch")=="chemistry"),key=lambda r:r["claim_id"])
 if len(rows)!=EXPECTED:raise SystemExit(f"expected {EXPECTED} admitted Chemistry claims, found {len(rows)}")
 obligations=read(ROOT/"census/chemistry_discipline_obligations.json")["obligations"];frozen={str(cid):o for o in obligations for cid in o.get("current_claim_ids",())}
 vector={f"{n:03d}":[] for n in range(1,13)};claim_vector=[];lines=sources=tampered=statuses=empirical_count=formal_count=0;terms=("adverse","unfavorable","unfavourable","absent","unavailable","unresolved","mismatch","inconsistent","failed","halt")
 for row in rows:
  cid=row["claim_id"];pkg=ROOT/"claims"/cid;reg=pkg/"registration.json";controls=pkg/"controls.json";receipt=ROOT/row["receipt_path"];cert=current_certificate(pkg,row["receipt_hash"])
  for p in (reg,controls,receipt,cert):
   if not p.is_file():raise SystemExit(f"missing evidence {p.relative_to(ROOT)}")
  receipt_data=read(receipt);control_data=read(controls).get("controls",())
  if receipt_data.get("receipt_hash")!=row["receipt_hash"] or not receipt_data.get("model_admitted") or not control_data or not all(x.get("passed") for x in control_data):raise SystemExit(f"invalid receipt/control surface for {cid}")
  empirical=pkg/"empirical_validation.json"
  if empirical.is_file():
   e=read(empirical);required=(e.get("passed") is True,e.get("evaluator_verified_seal") is True,e.get("target_opened_after_seal") is True,e.get("all_rows_preserved") is True,e.get("target_custody_certificate",{}).get("released_after_prediction_seal") is True,e.get("target_custody_certificate",{}).get("target_absent_until_prediction_seal") is True,receipt_data.get("closure_status") in {"depth_independent","finite_complete"},all(x.get("passed") for x in receipt_data.get("gate_results",())))
   if not all(required):raise SystemExit(f"incomplete empirical custody for {cid}")
   src=tuple(map(str,e.get("data_source_ids",())));meas=tuple(map(str,e.get("measurements",())))
   if not src or not meas:raise SystemExit(f"empty empirical vector for {cid}")
   t=sum(str(x.get("kind","")).startswith("tampered_") and x.get("passed") is True for x in control_data);status_surface=meas+(str(e.get("falsification_condition","")),);st=sum(any(term in x.casefold() for term in terms) for x in status_surface)
   if t!=2:raise SystemExit(f"expected two authoritative tamper controls in {cid}, found {t}")
   if cid in SUPPLEMENTAL_EMPIRICAL_SCOPE:
    obligation,override=SUPPLEMENTAL_EMPIRICAL_SCOPE[cid];members=override or vector_memberships(cid,obligation,len(src))
   else:
    obligation=obligation_from_certificate(cid,read(cert),frozen);members=vector_memberships(cid,obligation,len(src))
   empirical_count+=1
   external={"empirical_validation_path":empirical.relative_to(ROOT).as_posix(),"empirical_validation_sha256":digest(empirical),"measurement_receipt_hash":e["measurement_receipt_hash"],"prediction_seal_hash":e["target_custody_certificate"]["prediction_seal_hash"],"target_identity_hash":e["target_custody_certificate"]["registered_target_identity_hash"],"target_custody_certificate_hash":e["target_custody_certificate"]["certificate_hash"],"source_ids":src,"source_identity_count":len(src),"measurement_line_count":len(meas),"tampered_control_line_count":t,"explicit_status_line_count":st,"empirical_status":"source-custodied-post-seal-comparison"};lines+=len(meas);sources+=len(src);tampered+=t;statuses+=st
  else:
   if cid not in FORMAL_SCOPE:raise SystemExit(f"unregistered formal-only Chemistry row: {cid}")
   obligation,members,parent,boundary=FORMAL_SCOPE[cid];formal_count+=1;external={"empirical_validation_path":None,"empirical_parent_claim_id":parent,"source_ids":(),"source_identity_count":0,"measurement_line_count":0,"tampered_control_line_count":0,"explicit_status_line_count":1,"empirical_status":"formal-only-standing-or-operational-boundary","boundary":boundary};statuses+=1
  for n in members:vector[n].append(cid)
  claim_vector.append({"claim_id":cid,"obligation_id":obligation,"vector_memberships":members,"registration_path":reg.relative_to(ROOT).as_posix(),"registration_sha256":digest(reg),"certificate_path":cert.relative_to(ROOT).as_posix(),"certificate_sha256":digest(cert),"controls_path":controls.relative_to(ROOT).as_posix(),"controls_sha256":digest(controls),"receipt_path":receipt.relative_to(ROOT).as_posix(),"receipt_file_sha256":digest(receipt),"receipt_hash":row["receipt_hash"],"closure_scope":receipt_data.get("closure_status"),"model_admitted":True,"all_rows_preserved":True,**external})
 if any(not ids for ids in vector.values()):raise SystemExit("one or more VALID vectors is empty")
 repair=read(REPAIR_AUDIT);payload={"schema":"sft-v3-chemistry-valid-001-012-complete-empirical-vector/2","date":"2026-07-29","authority":"Maria Smith","provenance":"aggregate reconstruction of 263 individually admitted Chemistry claims; no new unknown-target blindness is claimed","non_retirement_rule":"A failed attempt remains evidence and earns no closure credit; each obligation remains active until distinct lawful success or complete structural impossibility proof.","base_admitted_chemistry_claim_count":len(rows),"empirically_compared_claim_count":empirical_count,"formal_only_explicit_boundary_count":formal_count,"base_measurement_line_count":lines,"base_source_identity_occurrence_count":sources,"base_tampered_control_line_count":tampered,"base_explicit_adverse_absent_unavailable_unresolved_or_halt_line_count":statuses,"all_base_claims_model_admitted":True,"all_base_claims_current_receipt_bound":True,"all_empirical_claims_target_opened_after_seal":True,"all_empirical_claims_rows_preserved":True,"all_formal_only_claims_explicitly_typed":True,"repair_audit_path":REPAIR_AUDIT.relative_to(ROOT).as_posix(),"repair_audit_sha256":digest(REPAIR_AUDIT),"reopened_scientific_surface_count":repair["atomic_empirical_file_audit"]["actual_reopened_scientific_surfaces"],"attempt_status_constitution":repair["attempt_status_constitution"],"vector_claim_ids":vector,"vector_claim_counts":{n:len(ids) for n,ids in vector.items()},"claims":claim_vector,"protected_engine_or_verifier_edit_made":False};payload["complete_vector_identity"]=canonical_digest(payload);OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"output":OUTPUT.relative_to(ROOT).as_posix(),"sha256":digest(OUTPUT),"claim_count":len(rows),"empirical":empirical_count,"formal_only":formal_count,"measurement_lines":lines,"source_occurrences":sources,"vector_counts":payload["vector_claim_counts"],"identity":payload["complete_vector_identity"]},indent=2))
if __name__=="__main__":main()
