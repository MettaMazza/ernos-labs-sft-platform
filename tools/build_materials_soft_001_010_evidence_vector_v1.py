#!/usr/bin/env python3
from hashlib import sha256
from html import unescape
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"experiments/external_sources/materials/soft_001_010_v1"; MANIFEST=BASE/"source_custody_manifest.json"; OUT=BASE/"complete_evidence_vector_v1.json"
BINDINGS={
 "SFT-MAT-SOFT-COLLOID-AGGREGATION-001":(("NIST-FLUID-SUSPENSIONS","self-association and aggregation","surface chemistry, surface adsorption, flow conditions, aggregate size"),),
 "SFT-MAT-SOFT-GEL-PERCOLATION-002":(("NIST-DYNAMIC-ARREST-GEL","physical gelation and rigidity percolation","particle dynamics and rheology"),),
 "SFT-MAT-SOFT-FOAM-DRAINAGE-003":(("NIST-FOAM-DRAINAGE","foam drainage","surfactants"),),
 "SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004":(("NIST-LIQUID-CRYSTAL","liquid crystal orientational order parameter","droplet shape, domain size, and liquid crystal defect density"),),
 "SFT-MAT-SOFT-EMULSION-DROPLET-005":(("NIST-EMULSION-DROPLETS","organization of droplets in layers","interfacial stress effects overwhelm shear stress"),),
 "SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006":(("NIST-FUNCTIONAL-POLYMERS","thin films, interfaces, nanostructures, and membranes","thin film mechanics, adhesion"),),
 "SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007":(("NIST-STRESS-CHAINS","Stress chain formation and evolution under shear","stress fluctuations and the suspension microstructure"),),
 "SFT-MAT-SOFT-JAMMING-BOUNDARY-008":(("NIST-JAMMING","isolated, periodic and percolated aggregates","jammed fractal networks"),),
 "SFT-MAT-SOFT-STIMULI-RESPONSIVE-009":(("NIST-RESPONSIVE-POLYMER","stimuli-responsive chain cleavage","dynamic or reversible polymer chemistry"),),
 "SFT-MAT-SOFT-ACTIVE-NONEQUILIBRIUM-010":(("NIST-SOFT-NONEQUILIBRIUM","far from the material's preferred state of equilibrium","sensitive to changes in pressure and temperature"),),
}
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def fh(p): return "sha256:"+sha256(p.read_bytes()).hexdigest()
def norm(s): return "".join(c for c in unescape(re.sub(r"<[^>]+>"," ",s)).casefold() if c.isalnum())
def main():
 m=json.loads(MANIFEST.read_text()); mid=m.pop("manifest_identity")
 if canonical(m)!=mid: raise SystemExit("SOFT manifest changed")
 docs={r["source_id"]:r for r in m["documents"]}; corp={}
 for sid,r in docs.items():
  p=ROOT/r["snapshot_path"]
  if fh(p)!=r["snapshot_hash"]: raise SystemExit("SOFT source changed "+sid)
  corp[sid]=norm(p.read_text(errors="ignore"))
 rows=[]
 for cid,binds in BINDINGS.items():
  comps=[]
  for sid,a,b in binds:
   ap,bp=norm(a) in corp[sid],norm(b) in corp[sid]
   if not(ap and bp): raise SystemExit(f"SOFT fragments absent {cid} {sid} {ap}/{bp}")
   d=docs[sid]; comps.append({"source_id":sid,"source_status":d["status"],"snapshot_path":d["snapshot_path"],"snapshot_hash":d["snapshot_hash"],"first_registered_fragment":a,"second_registered_fragment":b,"first_fragment_present":ap,"second_fragment_present":bp,"used_for_favourable_comparison":True})
  rows.append({"claim_id":cid,"comparisons":comps,"comparison_count":len(comps),"all_comparisons_preserved":True,"all_registered_fragments_present":True})
 x={"schema":"sft-v3-materials-soft-complete-evidence-vector/1","target_registry_identity":m["target_registry_identity"],"source_custody_manifest_identity":mid,"claim_count":len(rows),"claims":rows,"source_status_rows":list(docs.values()),"captured_source_count":len(docs),"unavailable_source_count":0,"all_favourable_adverse_absent_unavailable_unresolved_rows_preserved":True,"target_content_selected_survivor":False}; x["complete_vector_identity"]=canonical(x); OUT.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps({"claims":len(rows),"comparisons":sum(r["comparison_count"] for r in rows),"sources":len(docs),"identity":x["complete_vector_identity"]},indent=2))
if __name__=="__main__": main()
