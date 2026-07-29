#!/usr/bin/env python3
"""Capture the complete preregistered Materials MECH source set."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; REG=ROOT/"census/materials_mech_001_014_target_registry_v1.json"; OUT=ROOT/"experiments/external_sources/materials/mech_001_014_v1"
REMOTE=(
("NIST-VISCOELASTIC-SEALANT","https://www.nist.gov/publications/viscoelastic-characterization-sealant-materials","nist-viscoelastic-sealant.html"),
("NIST-RHEOLOGY","https://www.nist.gov/itl/math/rheology","nist-rheology.html"),
("NIST-FAILURE-PROPERTY-TESTS","https://nvlpubs.nist.gov/nistpubs/ir/2012/NIST.IR.7847.pdf","nist-failure-property-tests.pdf"),
("NIST-LUBRICATION-HANDBOOK","https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication640.pdf","nist-lubrication-handbook.pdf"),
("NIST-LUBRICANT-FILM","https://www.nist.gov/publications/nanotribology-application-coining-industry-ii-optimization-lubricant-film-formation","nist-lubricant-film.html"),
)
EXISTING=(
("NIST-MARTENSITIC-MATERIALS-STUDY","https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir83-1690.pdf","experiments/external_sources/materials/phase_001_010_v1/nist-martensitic-materials-study.pdf"),
("NIST-FATIGUE-FRACTURE","https://www.nist.gov/programs-projects/fatigue-and-fracture","experiments/external_sources/materials/snapshots/nist-fatigue-fracture.html"),
("NIST-NANOTRIBOLOGY","https://www.nist.gov/programs-projects/nanotribology","experiments/external_sources/materials/snapshots/nist-nanotribology.html"),
)
def digest(b): return "sha256:"+sha256(b).hexdigest()
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REG.read_bytes(); reg=json.loads(rb)
 if reg["target_count"]!=14 or reg["target_content_present"] is not False: raise SystemExit("MECH capture halted: registry changed")
 if OUT.exists(): raise SystemExit("refusing to overwrite MECH custody")
 OUT.mkdir(parents=True); docs=[]
 for sid,uri,name in REMOTE:
  req=Request(uri,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
  with urlopen(req,timeout=120) as response: body=response.read(); status=getattr(response,"status",200); content=response.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000: raise SystemExit(f"MECH capture halted: {sid} {status} {len(body)}")
  path=OUT/name;path.write_bytes(body);docs.append({"source_id":sid,"source_uri":uri,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":content,"status":"captured_post_registry","used_for_favourable_comparison":True})
 for sid,uri,rel in EXISTING:
  path=ROOT/rel;body=path.read_bytes();docs.append({"source_id":sid,"source_uri":uri,"snapshot_path":rel,"snapshot_hash":digest(body),"byte_count":len(body),"http_status":"preexisting","content_type":"preserved-official-snapshot","status":"captured_preexisting_official_snapshot","used_for_favourable_comparison":True})
 registered={s for t in reg["targets"] for s in t["source_identities"]}; captured={x["source_id"] for x in docs}
 if registered!=captured: raise SystemExit(f"MECH source mismatch {registered-captured} {captured-registered}")
 p={"schema":"sft-v3-materials-mech-source-custody/1","target_registry_path":REG.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":reg["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True};p["manifest_identity"]=canonical(p);(OUT/"source_custody_manifest.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"document_count":len(docs),"manifest_identity":p["manifest_identity"]},indent=2))
if __name__=="__main__": main()
