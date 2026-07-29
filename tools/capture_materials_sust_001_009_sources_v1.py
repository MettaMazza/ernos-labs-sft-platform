#!/usr/bin/env python3
"""Capture all registered SUST sources after the target registry is sealed."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/"census/materials_sust_001_009_target_registry_v1.json"; OUT=ROOT/"experiments/external_sources/materials/sust_001_009_v1"
REMOTE=(("NIST-LIFE-CYCLE-ASSESSMENT","https://www.nist.gov/critical-minerals-and-materials/databases-tools-capabilities","nist-life-cycle-assessment.html"),("NIST-CRITICAL-MINERALS-MATERIALS","https://www.nist.gov/critical-minerals-and-materials","nist-critical-minerals-materials.html"),("NIST-REGENERATIVE-MANUFACTURING","https://www.nist.gov/programs-projects/data-infrastructure-critical-material-recovery","nist-regenerative-manufacturing.html"),("NIST-CRITICAL-MATERIAL-RECOVERY","https://www.nist.gov/programs-projects/data-infrastructure-critical-material-recovery","nist-critical-material-recovery.html"),("NIST-MATERIAL-FLOW-CIRCULARITY","https://www.nist.gov/critical-minerals-and-materials/databases-tools-capabilities","nist-material-flow-circularity.html"),("NIST-MATERIALS-RESILIENCE","https://www.nist.gov/programs-projects/materials-and-structures-resilience-program","nist-materials-resilience.html"),("NIST-CIRCULAR-SAFETY","https://www.nist.gov/circular-economy","nist-circular-safety.html"),("NIST-CRITICAL-SUBSTITUTION","https://www.nist.gov/critical-minerals-and-materials/research-areas","nist-critical-substitution.html"),("NIST-CIRCULAR-END-OF-USE","https://www.nist.gov/circular-economy","nist-circular-end-of-use.html"))
def digest(b): return "sha256:"+sha256(b).hexdigest()
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REGISTRY.read_bytes(); reg=json.loads(rb)
 if reg["target_count"]!=9 or reg["target_content_present"] is not False or OUT.exists(): raise SystemExit("SUST custody halt")
 OUT.mkdir(parents=True); docs=[]
 for sid,url,name in REMOTE:
  with urlopen(Request(url,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as response: body=response.read(); status=getattr(response,"status",200); content_type=response.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000: raise SystemExit(f"SUST capture halt {sid} {status} {len(body)}")
  path=OUT/name; path.write_bytes(body); docs.append({"source_id":sid,"source_uri":url,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":content_type,"status":"captured_post_registry","used_for_favourable_comparison":True})
 if {s for t in reg["targets"] for s in t["source_identities"]}!={d["source_id"] for d in docs}: raise SystemExit("SUST source mismatch")
 v={"schema":"sft-v3-materials-sust-source-custody/1","target_registry_path":REGISTRY.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":reg["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True,"target_or_outcome_selected_source":False}; v["manifest_identity"]=canonical(v); (OUT/"source_custody_manifest.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n"); print(json.dumps({"documents":len(docs),"identity":v["manifest_identity"]},indent=2))
if __name__=="__main__": main()
