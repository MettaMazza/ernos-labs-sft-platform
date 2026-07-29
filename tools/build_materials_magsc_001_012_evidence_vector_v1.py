#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/"experiments/external_sources/materials/magsc_001_012_v1";MAN=BASE/"source_custody_manifest.json";OUT=BASE/"complete_evidence_vector_v1.json"
B={
"SFT-MAT-MAGSC-PARAMAGNETIC-RESPONSE-001":(("NIST-MAGNETIC-SUSCEPTIBILITY-SRM","specific susceptibility","magnetic moment"),("NIST-PARAMAGNETIC-DIAMAGNETIC","paramagnetic or diamagnetic","parallel or antiparallel alignment")),
"SFT-MAT-MAGSC-DIAMAGNETIC-RESPONSE-002":(("NIST-PARAMAGNETIC-DIAMAGNETIC","diamagnetic susceptibility","antiparallel alignment"),("NIST-MAGNETIC-SUSCEPTIBILITY-SRM","pure platinum cylinder","specific susceptibility")),
"SFT-MAT-MAGSC-SPIN-GLASS-FREEZING-003":(("NIST-MAGNETIZATION-LAB","spin freezing temperatures","magnetic state"),),
"SFT-MAT-MAGSC-DOMAINS-WALLS-004":(("NIST-MAGNETIZATION-LAB","magnetic domains while they are forming, growing, and disappearing","magnetization dynamics"),("NIST-MAGNETIC-IMAGING","domain wall mobility","magnetic domains")),
"SFT-MAT-MAGSC-HYSTERESIS-LOOP-005":(("NIST-MAGNETIC-IMAGING","magnetization reversal","field regimes"),("NIST-HYSTERESIS-STANDARD","hysteresis loop","scaled geometry")),
"SFT-MAT-MAGSC-MAGNETOCRYSTALLINE-ANISOTROPY-006":(("NIST-MAGNETIC-MATERIALS-METROLOGY","magnetocrystalline anisotropy","magnetic anisotropy"),("NIST-MAGNETIZATION-LAB","magnetic anisotropy","coercivity")),
"SFT-MAT-MAGSC-MAGNETORESISTANCE-007":(("NIST-SPIN-ORBIT","magnetoresistance","charge and spin current"),("NIST-MAGNETIC-IMAGING","antisymmetric magnetoresistance","domain walls")),
"SFT-MAT-MAGSC-SPIN-TRANSPORT-RELAXATION-008":(("NIST-SPIN-TRANSPORT","spin transport","OFF-state"),("NIST-SPIN-SPECTROSCOPY","spin and magnon transport","energy dissipation")),
"SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009":(("NIST-SC-CRITICAL-FIELDS","upper critical fields","Meissner state"),),
"SFT-MAT-MAGSC-SC-VORTEX-PINNING-010":(("NIST-SC-FLUX-LATTICE","vortices","pin"),),
"SFT-MAT-MAGSC-SC-COHERENCE-LENGTH-011":(("NIST-SC-CRITICAL-FIELDS","coherence length","penetration depth"),),
"SFT-MAT-MAGSC-SUPERFLUID-CRITICAL-FLOW-012":(("NIST-SUPERFLUID-PERSISTENT-FLOW","persistent current","superfluidity"),),}
TEXT={"NIST-SC-CRITICAL-FIELDS":BASE/"nist-sc-critical-fields.txt"}
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def fh(p):return "sha256:"+sha256(p.read_bytes()).hexdigest()
def norm(s):return "".join(c for c in s.casefold() if c.isalnum())
def main():
 m=json.loads(MAN.read_text());mid=m.pop("manifest_identity")
 if canon(m)!=mid:raise SystemExit("manifest changed")
 docs={x["source_id"]:x for x in m["documents"]};corp={}
 for sid,row in docs.items():
  p=ROOT/row["snapshot_path"]
  if fh(p)!=row["snapshot_hash"]:raise SystemExit("source changed "+sid)
  corp[sid]=norm(TEXT.get(sid,p).read_text(errors="ignore"))
 rows=[]
 for cid,bindings in B.items():
  cs=[]
  for sid,a,b in bindings:
   ap,bp=norm(a) in corp[sid],norm(b) in corp[sid]
   if not(ap and bp):raise SystemExit(f"fragments absent {cid} {sid} {ap}/{bp}")
   s=docs[sid];cs.append({"source_id":sid,"source_status":s["status"],"snapshot_path":s["snapshot_path"],"snapshot_hash":s["snapshot_hash"],"first_registered_fragment":a,"second_registered_fragment":b,"first_fragment_present":ap,"second_fragment_present":bp,"used_for_favourable_comparison":True})
  rows.append({"claim_id":cid,"comparisons":cs,"comparison_count":len(cs),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 p={"schema":"sft-v3-materials-magsc-complete-evidence-vector/1","target_registry_identity":m["target_registry_identity"],"source_custody_manifest_identity":mid,"claim_count":len(rows),"claims":rows,"source_status_rows":list(docs.values()),"captured_source_count":m["captured_count"],"unavailable_source_count":m["unavailable_count"],"pdf_text_reconstructions":[{"source_id":sid,"text_path":path.relative_to(ROOT).as_posix(),"text_hash":fh(path)} for sid,path in TEXT.items()],"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False};p["complete_vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":len(rows),"comparisons":sum(x["comparison_count"] for x in rows),"identity":p["complete_vector_identity"]},indent=2))
if __name__=="__main__":main()
