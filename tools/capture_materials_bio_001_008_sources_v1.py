#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/"census/materials_bio_001_008_target_registry_v1.json"; OUT=ROOT/"experiments/external_sources/materials/bio_001_008_v1"
REMOTE=(("NIST-BIOMATERIAL-MEASUREMENTS","https://www.nist.gov/mml/bbd/core-capabilities/biomaterial-measurements","nist-biomaterial-measurements.html"),("NIST-BIORESORPTION-RATE","https://www.nist.gov/publications/vitro-model-studying-bioresorption-rate-calcium-phosphate-bone-graft-materials","nist-bioresorption-rate.html"),("NIST-REFERENCE-SCAFFOLDS","https://www.nist.gov/publications/nist-reference-material-scaffolds-tissue-engineering","nist-reference-scaffolds.html"),("NIST-CELL-MATRIX","https://www.nist.gov/programs-projects/multiparametric-measurement-and-analysis-cell-behavior-extracellular-matrices","nist-cell-matrix.html"),("NIST-BONE-IMPLANT-LAYERS","https://www.nist.gov/news-events/news/2007/08/layered-approach-may-yield-stronger-more-successful-bone-implants","nist-bone-implant-layers.html"),("NIST-CONTROLLED-PROTEIN-RELEASE","https://www.nist.gov/node/611541","nist-controlled-protein-release.html"),("NIST-HYDROXYAPATITE","https://www.nist.gov/publications/preparation-and-comprehensive-characterization-calicum-hydroxyapatite-reference","nist-hydroxyapatite.html"),("NIST-BIOFABRICATION-METROLOGY","https://www.nist.gov/publications/measurement-needs-biofabrication-tissue-engineered-medical-products-workshop-report","nist-biofabrication-metrology.html"))
def digest(b): return "sha256:"+sha256(b).hexdigest()
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REGISTRY.read_bytes(); r=json.loads(rb)
 if r["target_count"]!=8 or r["target_content_present"] is not False: raise SystemExit("BIO registry changed")
 if OUT.exists(): raise SystemExit("refusing overwrite")
 OUT.mkdir(parents=True); docs=[]
 for sid,url,name in REMOTE:
  with urlopen(Request(url,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as q: body=q.read(); status=getattr(q,"status",200); typ=q.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000: raise SystemExit(f"BIO capture halt {sid} {status} {len(body)}")
  p=OUT/name; p.write_bytes(body); docs.append({"source_id":sid,"source_uri":url,"snapshot_path":p.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":typ,"status":"captured_post_registry","used_for_favourable_comparison":True})
 if {s for t in r["targets"] for s in t["source_identities"]}!={d["source_id"] for d in docs}: raise SystemExit("BIO source mismatch")
 x={"schema":"sft-v3-materials-bio-source-custody/1","target_registry_path":REGISTRY.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":r["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True,"target_or_outcome_selected_source":False}; x["manifest_identity"]=canonical(x); (OUT/"source_custody_manifest.json").write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps({"documents":len(docs),"identity":x["manifest_identity"]},indent=2))
if __name__=="__main__": main()
