#!/usr/bin/env python3
"""Freeze the complete factual pre-VALID Materials evidence surface."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"experiments/external_sources/materials/valid_001_012_complete_empirical_vector_v1.json"; EXPECTED=271
def read(p): return json.loads(p.read_text())
def digest(p): return "sha256:"+sha256(p.read_bytes()).hexdigest()
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def current_certificate(pkg,receipt_hash):
 rows=[p for p in sorted(pkg.glob("certificate*.json")) if read(p).get("engine_receipt_hash")==receipt_hash]
 if len(rows)!=1: raise SystemExit(f"{pkg.name} current certificate count {len(rows)}")
 return rows[0]
def obligation(cert,cid,frozen):
 if cert.get("materials_obligation"): return cert["materials_obligation"]
 if cid in frozen: return frozen[cid]["obligation_id"]
 raise SystemExit("unowned Materials claim "+cid)
def memberships(oid,source_count):
 family=oid.split("-")[3]; rows={"CRYS":"001","MICRO":"002","PHASE":"003","MECH":"004","THERM":"005","ELEC":"006","MAGSC":"007","OPT":"008"}; out={"011","012"}
 if family in rows: out.add(rows[family])
 if family in {"CLASS","PROC"}: out.add("009")
 if source_count>=2: out.add("010")
 return tuple(sorted(out))
def main():
 if OUT.exists(): raise SystemExit("Materials VALID evidence vector already frozen")
 census=read(ROOT/"census/claims.json"); base=sorted((r for r in census["claims"] if r.get("branch")=="materials"),key=lambda r:r["claim_id"])
 if len(base)!=EXPECTED or any(not r.get("model_admitted") for r in base): raise SystemExit(f"expected {EXPECTED} admitted Materials claims, found {len(base)}")
 obligations=read(ROOT/"census/materials_discipline_obligations.json")["obligations"]; frozen={str(cid):o for o in obligations for cid in o.get("current_claim_ids",())}
 vectors={f"{n:03d}":[] for n in range(1,13)}; claims=[]; lines=sources=tampered=statuses=0; terms=("adverse","unfavorable","unfavourable","absent","unavailable","unresolved","mismatch","inconsistent","failed","halt","boundary")
 for row in base:
  cid=row["claim_id"]; pkg=ROOT/"claims"/cid; reg=pkg/"registration.json"; controls=pkg/"controls.json"; empirical=pkg/"empirical_validation.json"; receipt=ROOT/row["receipt_path"]; cert=current_certificate(pkg,row["receipt_hash"])
  for p in (reg,controls,empirical,receipt,cert):
   if not p.is_file(): raise SystemExit(f"missing Materials evidence {p.relative_to(ROOT)}")
  r=read(receipt); c=read(controls).get("controls",()); e=read(empirical)
  required=(r.get("receipt_hash")==row["receipt_hash"],r.get("model_admitted") is True,r.get("closure_status") in {"depth_independent","finite_complete"},bool(c),all(x.get("passed") for x in c),e.get("passed") is True,e.get("evaluator_verified_seal") is True,e.get("target_opened_after_seal") is True,e.get("all_rows_preserved") is True,e.get("target_custody_certificate",{}).get("released_after_prediction_seal") is True,e.get("target_custody_certificate",{}).get("target_absent_until_prediction_seal") is True)
  if not all(required): raise SystemExit("incomplete Materials custody "+cid)
  src=tuple(map(str,e.get("data_source_ids",()))); meas=tuple(map(str,e.get("measurements",())))
  if not src or not meas: raise SystemExit("empty Materials empirical vector "+cid)
  t=sum(str(x.get("kind","")).startswith("tampered_") and x.get("passed") is True for x in c)
  if t!=2: raise SystemExit(f"expected two tamper controls {cid}, found {t}")
  st=sum(any(term in x.casefold() for term in terms) for x in meas+(str(e.get("falsification_condition","")),)); certdata=read(cert); oid=obligation(certdata,cid,frozen); member=memberships(oid,len(src))
  for n in member: vectors[n].append(cid)
  claims.append({"claim_id":cid,"obligation_id":oid,"vector_memberships":member,"registration_path":reg.relative_to(ROOT).as_posix(),"registration_sha256":digest(reg),"certificate_path":cert.relative_to(ROOT).as_posix(),"certificate_sha256":digest(cert),"controls_path":controls.relative_to(ROOT).as_posix(),"controls_sha256":digest(controls),"empirical_validation_path":empirical.relative_to(ROOT).as_posix(),"empirical_validation_sha256":digest(empirical),"receipt_path":receipt.relative_to(ROOT).as_posix(),"receipt_file_sha256":digest(receipt),"receipt_hash":row["receipt_hash"],"closure_scope":r["closure_status"],"measurement_receipt_hash":e["measurement_receipt_hash"],"source_ids":src,"source_identity_count":len(src),"measurement_line_count":len(meas),"tampered_control_line_count":t,"explicit_status_line_count":st,"empirical_status":"source-custodied-post-seal-comparison","model_admitted":True,"all_rows_preserved":True}); lines+=len(meas); sources+=len(src); tampered+=t; statuses+=st
 if any(not ids for ids in vectors.values()): raise SystemExit("one or more Materials VALID vectors is empty")
 v={"schema":"sft-v3-materials-valid-001-012-complete-empirical-vector/1","date":"2026-07-29","authority":"Maria Smith","provenance":"aggregate reconstruction of 271 individually admitted Materials claims; no new unknown-target blindness is claimed","non_retirement_rule":"A failed attempt remains evidence and earns no closure credit; each obligation remains active until distinct lawful success or complete structural impossibility proof.","base_admitted_materials_claim_count":len(base),"empirically_compared_claim_count":len(base),"formal_only_explicit_boundary_count":0,"base_measurement_line_count":lines,"base_source_identity_occurrence_count":sources,"base_tampered_control_line_count":tampered,"base_explicit_adverse_absent_unavailable_unresolved_or_halt_line_count":statuses,"all_base_claims_model_admitted":True,"all_base_claims_current_receipt_bound":True,"all_empirical_claims_target_opened_after_seal":True,"all_empirical_claims_rows_preserved":True,"vector_claim_ids":vectors,"vector_claim_counts":{n:len(ids) for n,ids in vectors.items()},"claims":claims,"protected_engine_or_verifier_edit_made":False}; v["complete_vector_identity"]=canonical(v); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n"); print(json.dumps({"claims":len(base),"measurement_lines":lines,"source_occurrences":sources,"counts":v["vector_claim_counts"],"identity":v["complete_vector_identity"],"file_hash":digest(OUT)},indent=2))
if __name__=="__main__": main()
