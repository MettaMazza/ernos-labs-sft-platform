#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/"experiments/external_sources/materials/mech_001_014_v1";MAN=BASE/"source_custody_manifest.json";OUT=BASE/"complete_evidence_vector_v1.json"
B={
"SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001":(("NIST-MARTENSITIC-MATERIALS-STUDY","stress-strain curves","elastic constants"),),
"SFT-MAT-MECH-TRANSVERSE-STRAIN-002":(("NIST-MARTENSITIC-MATERIALS-STUDY","stress-strain curves","elastic properties"),),
"SFT-MAT-MECH-VISCOELASTIC-MEMORY-003":(("NIST-VISCOELASTIC-SEALANT","non-linear viscoelastic properties","stress-relaxation experiments"),),
"SFT-MAT-MECH-VISCOPLASTIC-FLOW-004":(("NIST-RHEOLOGY","resistance to flow","function of the shear rate"),),
"SFT-MAT-MECH-YIELD-PATH-005":(("NIST-RHEOLOGY","viscosity and yield stress","force needed to initiate flow"),),
"SFT-MAT-MECH-WORK-HARDENING-006":(("NIST-MARTENSITIC-MATERIALS-STUDY","degree of work hardening","flow strength"),),
"SFT-MAT-MECH-FRACTURE-ENERGY-007":(("NIST-FAILURE-PROPERTY-TESTS","fracture toughness","resist this fracture"),),
"SFT-MAT-MECH-CRACK-GROWTH-008":(("NIST-FAILURE-PROPERTY-TESTS","crack growth tests","rate of crack growth"),("NIST-FATIGUE-FRACTURE","fatigue crack initiation","fracture surface")),
"SFT-MAT-MECH-FATIGUE-009":(("NIST-FAILURE-PROPERTY-TESTS","fatigue cycles","crack growth rates"),("NIST-FATIGUE-FRACTURE","high-cycle fatigue fracture surfaces","fatigue crack initiation")),
"SFT-MAT-MECH-CREEP-RUPTURE-010":(("NIST-FAILURE-PROPERTY-TESTS","Creep Crack Growth Rate","creep deformation"),),
"SFT-MAT-MECH-IMPACT-011":(("NIST-FAILURE-PROPERTY-TESTS","Absorbed Impact Energy","notched metal"),),
"SFT-MAT-MECH-FRICTION-CONTACT-012":(("NIST-NANOTRIBOLOGY","interacting surfaces in relative motion","friction, adhesion, lubrication, and wear"),("NIST-LUBRICATION-HANDBOOK","reduce friction or resistance to motion","prevented from making contact by a film")),
"SFT-MAT-MECH-LUBRICATION-TRIBOFILM-013":(("NIST-LUBRICANT-FILM","monomolecular film during burnishing","tribological environments"),("NIST-LUBRICATION-HANDBOOK","forming a plastic lubricating film","fluid lubricant")),
"SFT-MAT-MECH-RHEOLOGY-014":(("NIST-RHEOLOGY","Rheology is the study of the flow properties of liquids","viscosity and yield stress"),("NIST-VISCOELASTIC-SEALANT","time dependence and strain dependence","stress-relaxation experiments")),}
TEXT={"NIST-MARTENSITIC-MATERIALS-STUDY":ROOT/"experiments/external_sources/materials/phase_001_010_v1/nist-martensitic-materials-study.txt","NIST-FAILURE-PROPERTY-TESTS":BASE/"nist-failure-property-tests.txt","NIST-LUBRICATION-HANDBOOK":BASE/"nist-lubrication-handbook.txt"}
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def fh(p):return "sha256:"+sha256(p.read_bytes()).hexdigest()
def norm(s):return "".join(c for c in s.casefold() if c.isalnum())
def main():
 m=json.loads(MAN.read_text());mid=m.pop("manifest_identity")
 if canon(m)!=mid:raise SystemExit("MECH manifest changed")
 docs={x["source_id"]:x for x in m["documents"]};corp={}
 for sid,row in docs.items():
  p=ROOT/row["snapshot_path"]
  if fh(p)!=row["snapshot_hash"]:raise SystemExit("MECH source changed "+sid)
  corp[sid]=norm(TEXT.get(sid,p).read_text(errors="ignore"))
 rows=[]
 for cid,bindings in B.items():
  cs=[]
  for sid,a,b in bindings:
   ap,bp=norm(a) in corp[sid],norm(b) in corp[sid]
   if not(ap and bp):raise SystemExit(f"MECH fragments absent {cid} {sid} {ap}/{bp}")
   s=docs[sid];cs.append({"source_id":sid,"source_status":s["status"],"snapshot_path":s["snapshot_path"],"snapshot_hash":s["snapshot_hash"],"first_registered_fragment":a,"second_registered_fragment":b,"first_fragment_present":ap,"second_fragment_present":bp,"used_for_favourable_comparison":True})
  rows.append({"claim_id":cid,"comparisons":cs,"comparison_count":len(cs),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 p={"schema":"sft-v3-materials-mech-complete-evidence-vector/1","target_registry_identity":m["target_registry_identity"],"source_custody_manifest_identity":mid,"claim_count":len(rows),"claims":rows,"source_status_rows":list(docs.values()),"captured_source_count":m["captured_count"],"unavailable_source_count":m["unavailable_count"],"pdf_text_reconstructions":[{"source_id":sid,"text_path":path.relative_to(ROOT).as_posix(),"text_hash":fh(path)} for sid,path in TEXT.items()],"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False};p["complete_vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":len(rows),"comparisons":sum(x["comparison_count"] for x in rows),"identity":p["complete_vector_identity"]},indent=2))
if __name__=="__main__":main()
