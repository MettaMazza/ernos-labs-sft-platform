#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/"census/materials_surf_001_008_target_registry_v1.json"; OUT=ROOT/"experiments/external_sources/materials/surf_001_008_v1"
REMOTE=(("NIST-POLYMER-SURFACE-INTERFACE","https://www.nist.gov/el/mssd/polymer-surfaceinterface-consortium","nist-polymer-surface-interface.html"),("NIST-WETTING-WRINKLED-SURFACES","https://www.nist.gov/publications/wetting-behavior-microscale-wrinkled-surfaces","nist-wetting-wrinkled-surfaces.html"),("NIST-ADHESION-ENERGY-DISSIPATION","https://www.nist.gov/publications/model-adhesion-based-energy-dissipation-during-friction","nist-adhesion-energy-dissipation.html"),("NIST-COATING-MICROSTRUCTURE","https://www.nist.gov/publications/investigation-relationship-between-microstructure-and-appearance-properties-coating","nist-coating-microstructure.html"),("NIST-COATING-SURFACE-ROUGHNESS","https://www.nist.gov/publications/effects-bond-coat-surface-roughness-residual-stresses-thermal-barrier-coating-systems","nist-coating-surface-roughness.html"),("NIST-POLYMER-SURFACE-CHEMISTRY","https://www.nist.gov/el/mssd/polymer-surfaceinterface-consortium","nist-polymer-surface-chemistry.html"),("NIST-TRIBOLOGICAL-COATINGS","https://www.nist.gov/publications/nanostructured-multifunctional-tribological-coatings","nist-tribological-coatings.html"),("NIST-EDGE-DELAMINATION","https://www.nist.gov/publications/combinatorial-edge-delamination-test-thin-film-adhesion-concept-procedure-results","nist-edge-delamination.html"))
def digest(body): return "sha256:"+sha256(body).hexdigest()
def canonical(value): return "sha256:"+sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REGISTRY.read_bytes(); registry=json.loads(rb)
 if registry["target_count"]!=8 or registry["target_content_present"] is not False: raise SystemExit("SURF registry changed")
 if OUT.exists(): raise SystemExit("refusing overwrite")
 OUT.mkdir(parents=True); documents=[]
 for source_id,url,name in REMOTE:
  with urlopen(Request(url,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as response: body=response.read(); status=getattr(response,"status",200); content_type=response.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000: raise SystemExit(f"SURF capture halt {source_id} {status} {len(body)}")
  path=OUT/name; path.write_bytes(body); documents.append({"source_id":source_id,"source_uri":url,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":content_type,"status":"captured_post_registry","used_for_favourable_comparison":True})
 if {source for target in registry["targets"] for source in target["source_identities"]}!={document["source_id"] for document in documents}: raise SystemExit("SURF source mismatch")
 value={"schema":"sft-v3-materials-surf-source-custody/1","target_registry_path":REGISTRY.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":registry["registry_identity"],"documents":documents,"document_count":len(documents),"captured_count":len(documents),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True,"target_or_outcome_selected_source":False}; value["manifest_identity"]=canonical(value); (OUT/"source_custody_manifest.json").write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); print(json.dumps({"documents":len(documents),"identity":value["manifest_identity"]},indent=2))
if __name__=="__main__": main()

