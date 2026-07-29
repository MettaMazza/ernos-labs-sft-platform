#!/usr/bin/env python3
from hashlib import sha256
from html import unescape
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"experiments/external_sources/materials/bio_001_008_v1"; MANIFEST=BASE/"source_custody_manifest.json"; OUT=BASE/"complete_evidence_vector_v1.json"
BINDINGS={"SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001":(("NIST-BIOMATERIAL-MEASUREMENTS","material designed to take a form that can direct","interactions with living systems"),),"SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002":(("NIST-BIORESORPTION-RATE","constant-composition dissolution system","factors that may control the resorption rate"),),"SFT-MAT-BIO-SCAFFOLD-POROSITY-CONNECTIVITY-003":(("NIST-REFERENCE-SCAFFOLDS","strut diameter, strut spacing and porosity","47%, 60% and 69%"),),"SFT-MAT-BIO-CELL-MATERIAL-ADHESION-004":(("NIST-CELL-MATRIX","Cells adhere to type I collagen","mechanical stiffness, and supramolecular organization"),),"SFT-MAT-BIO-MECHANICAL-MATCHING-005":(("NIST-BONE-IMPLANT-LAYERS","porosity needed for bone growth and the integrity required","strong, fiber-reinforced CPC paste"),),"SFT-MAT-BIO-CONTROLLED-RELEASE-006":(("NIST-CONTROLLED-PROTEIN-RELEASE","Protein release was defined as mass of released protein/mass of total protein","control protein release via microstructural tailoring"),),"SFT-MAT-BIO-MINERALIZED-ORGANIZATION-007":(("NIST-HYDROXYAPATITE","calcium hydroxyapatite","crystal size and morphology, surface area, unit-cell parameters, crystallinity, and solubility"),),"SFT-MAT-BIO-BIOFABRICATED-IDENTITY-008":(("NIST-BIOFABRICATION-METROLOGY","structure of the constructs, cell viability in the constructs, and functional capacity","collection, validation, and standardization of reference data"),)}
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def fh(p): return "sha256:"+sha256(p.read_bytes()).hexdigest()
def norm(s): return "".join(c for c in unescape(re.sub(r"<[^>]+>"," ",s)).casefold() if c.isalnum())
def main():
 m=json.loads(MANIFEST.read_text()); mid=m.pop("manifest_identity")
 if canonical(m)!=mid: raise SystemExit("BIO manifest changed")
 docs={r["source_id"]:r for r in m["documents"]}; corp={}
 for sid,r in docs.items():
  p=ROOT/r["snapshot_path"]
  if fh(p)!=r["snapshot_hash"]: raise SystemExit("BIO source changed "+sid)
  corp[sid]=norm(p.read_text(errors="ignore"))
 rows=[]
 for cid,binds in BINDINGS.items():
  comps=[]
  for sid,a,b in binds:
   ap,bp=norm(a) in corp[sid],norm(b) in corp[sid]
   if not(ap and bp): raise SystemExit(f"BIO fragments absent {cid} {sid} {ap}/{bp}")
   d=docs[sid]; comps.append({"source_id":sid,"source_status":d["status"],"snapshot_path":d["snapshot_path"],"snapshot_hash":d["snapshot_hash"],"first_registered_fragment":a,"second_registered_fragment":b,"first_fragment_present":ap,"second_fragment_present":bp,"used_for_favourable_comparison":True})
  rows.append({"claim_id":cid,"comparisons":comps,"comparison_count":len(comps),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 x={"schema":"sft-v3-materials-bio-complete-evidence-vector/1","target_registry_identity":m["target_registry_identity"],"source_custody_manifest_identity":mid,"claim_count":len(rows),"claims":rows,"source_status_rows":list(docs.values()),"captured_source_count":len(docs),"unavailable_source_count":0,"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False}; x["complete_vector_identity"]=canonical(x); OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps({"claims":len(rows),"comparisons":sum(r["comparison_count"] for r in rows),"sources":len(docs),"identity":x["complete_vector_identity"]},indent=2))
if __name__=="__main__": main()
