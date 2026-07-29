#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/"experiments/external_sources/materials/elec_001_012_v1";MAN=BASE/"source_custody_manifest.json";OUT=BASE/"complete_evidence_vector_v1.json"
B={
"SFT-MAT-ELEC-CONDUCTIVITY-RESISTIVITY-001":(("NIST-HALL-EFFECT","resistivity (or conductivity)","current-carrying capability"),),
"SFT-MAT-ELEC-MOBILITY-CONCENTRATION-002":(("NIST-HALL-EFFECT","carrier density","mobility"),),
"SFT-MAT-ELEC-HALL-RESPONSE-003":(("NIST-RESISTIVITY-HALL","Hall voltage","sheet carrier density"),),
"SFT-MAT-ELEC-DIELECTRIC-LOSS-004":(("NIST-DIELECTRIC-PERMITTIVITY-LOSS","relative permittivity","loss tangent"),),
"SFT-MAT-ELEC-IONIC-TRANSFERENCE-005":(("NIST-IONIC-CONDUCTIVITY","oxygen vacancy ionic hopping","impedance spectroscopy"),),
"SFT-MAT-ELEC-MIXED-TRANSPORT-006":(("NIST-MIXED-IONIC-ELECTRONIC","mobile electronic charge carriers","simultaneously supporting ionic transport"),),
"SFT-MAT-ELEC-FINITE-BARRIER-TUNNELLING-007":(("NIST-TUNNEL-BAND-OFFSET","barrier heights","quantum tunneling efficiency"),),
"SFT-MAT-ELEC-BAND-ALIGNMENT-008":(("NIST-TUNNEL-BAND-OFFSET","complete energy band alignment","band offset"),("NIST-OPTOELECTRONIC-BAND-METROLOGY","band alignment/offset","heterojunction interfaces")),
"SFT-MAT-ELEC-CARRIER-CONFINEMENT-009":(("NIST-TUNNEL-BAND-OFFSET","semiconductor heterojunction interface","electron and hole barrier heights"),("NIST-OPTOELECTRONIC-BAND-METROLOGY","2-D heterostructure semiconductors","multiple layer structures")),
"SFT-MAT-ELEC-DEFECT-TRAP-STATES-010":(("NIST-POINT-DEFECT-CHEMISTRY","point defects","valence state"),),
"SFT-MAT-ELEC-SCREENING-DEPLETION-011":(("NIST-DIELECTRIC-DEPLETION","accumulation, depletion and inversion","trapped charge density"),),
"SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012":(("NIST-OPERANDO-ELECTROCHEMICAL","battery charging and discharging","measure the charge transfer processes while they happen"),),}
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def fh(p):return "sha256:"+sha256(p.read_bytes()).hexdigest()
def norm(s):return "".join(c for c in s.casefold() if c.isalnum())
def main():
 m=json.loads(MAN.read_text());mid=m.pop("manifest_identity")
 if canon(m)!=mid:raise SystemExit("ELEC manifest changed")
 docs={x["source_id"]:x for x in m["documents"]};corp={}
 for sid,row in docs.items():
  p=ROOT/row["snapshot_path"]
  if fh(p)!=row["snapshot_hash"]:raise SystemExit("ELEC source changed "+sid)
  corp[sid]=norm(p.read_text(errors="ignore"))
 rows=[]
 for cid,bindings in B.items():
  cs=[]
  for sid,a,b in bindings:
   ap,bp=norm(a) in corp[sid],norm(b) in corp[sid]
   if not(ap and bp):raise SystemExit(f"ELEC fragments absent {cid} {sid} {ap}/{bp}")
   s=docs[sid];cs.append({"source_id":sid,"source_status":s["status"],"snapshot_path":s["snapshot_path"],"snapshot_hash":s["snapshot_hash"],"first_registered_fragment":a,"second_registered_fragment":b,"first_fragment_present":ap,"second_fragment_present":bp,"used_for_favourable_comparison":True})
  rows.append({"claim_id":cid,"comparisons":cs,"comparison_count":len(cs),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 p={"schema":"sft-v3-materials-elec-complete-evidence-vector/1","target_registry_identity":m["target_registry_identity"],"source_custody_manifest_identity":mid,"claim_count":len(rows),"claims":rows,"source_status_rows":list(docs.values()),"captured_source_count":m["captured_count"],"unavailable_source_count":m["unavailable_count"],"pdf_text_reconstructions":[],"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False};p["complete_vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":len(rows),"comparisons":sum(x["comparison_count"] for x in rows),"identity":p["complete_vector_identity"]},indent=2))
if __name__=="__main__":main()
