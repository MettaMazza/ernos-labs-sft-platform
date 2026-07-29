#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/"census/materials_soft_001_010_target_registry_v1.json"; OUT=ROOT/"experiments/external_sources/materials/soft_001_010_v1"
REMOTE=(
 ("NIST-FLUID-SUSPENSIONS","https://www.nist.gov/programs-projects/fluid-suspensions-and-emulsions","nist-fluid-suspensions.html"),
 ("NIST-DYNAMIC-ARREST-GEL","https://www.nist.gov/publications/dynamic-arrest-adhesive-hard-rod-dispersions","nist-dynamic-arrest-gel.html"),
 ("NIST-FOAM-DRAINAGE","https://firedoc.nist.gov/article/03czXYQBWEcjUZEYGv8r","nist-foam-drainage.html"),
 ("NIST-LIQUID-CRYSTAL","https://math.nist.gov/mcsd/Reports/96/yearly/node12.html","nist-liquid-crystal.html"),
 ("NIST-EMULSION-DROPLETS","https://www.nist.gov/publications/droplet-microstructure-and-string-stability-sheared-emulsions-role-finite-size-effects","nist-emulsion-droplets.html"),
 ("NIST-FUNCTIONAL-POLYMERS","https://www.nist.gov/mml/materials-science-and-engineering-division/functional-polymers-group","nist-functional-polymers.html"),
 ("NIST-STRESS-CHAINS","https://www.nist.gov/publications/stress-chains-formation-under-shear-concentrated-suspension","nist-stress-chains.html"),
 ("NIST-JAMMING","https://www.nist.gov/publications/jamming-carbon-nanotube-suspensions","nist-jamming.html"),
 ("NIST-RESPONSIVE-POLYMER","https://www.nist.gov/people/sara-orski","nist-responsive-polymer.html"),
 ("NIST-SOFT-NONEQUILIBRIUM","https://www.nist.gov/news-events/news/2012/07/new-nist-led-consortium-aims-improve-process-making-soft-materials","nist-soft-nonequilibrium.html"),
)
def digest(b): return "sha256:"+sha256(b).hexdigest()
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REGISTRY.read_bytes(); r=json.loads(rb)
 if r["target_count"]!=10 or r["target_content_present"] is not False: raise SystemExit("SOFT registry changed")
 if OUT.exists(): raise SystemExit("refusing overwrite")
 OUT.mkdir(parents=True); docs=[]
 for sid,url,name in REMOTE:
  with urlopen(Request(url,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as q: body=q.read(); status=getattr(q,"status",200); typ=q.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000: raise SystemExit(f"SOFT capture halt {sid} {status} {len(body)}")
  p=OUT/name; p.write_bytes(body); docs.append({"source_id":sid,"source_uri":url,"snapshot_path":p.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":typ,"status":"captured_post_registry","used_for_favourable_comparison":True})
 if {s for t in r["targets"] for s in t["source_identities"]}!={d["source_id"] for d in docs}: raise SystemExit("SOFT source mismatch")
 x={"schema":"sft-v3-materials-soft-source-custody/1","target_registry_path":REGISTRY.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":r["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True,"target_or_outcome_selected_source":False}; x["manifest_identity"]=canonical(x); (OUT/"source_custody_manifest.json").write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps({"documents":len(docs),"identity":x["manifest_identity"]},indent=2))
if __name__=="__main__": main()
