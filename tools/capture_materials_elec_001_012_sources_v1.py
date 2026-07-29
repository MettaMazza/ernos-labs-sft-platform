#!/usr/bin/env python3
"""Capture the complete preregistered Materials ELEC source set."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/materials_elec_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/materials/elec_001_012_v1"
REMOTE=(
("NIST-HALL-EFFECT","https://www.nist.gov/pml/nanoscale-device-characterization-division/popular-links/hall-effect/hall-effect","nist-hall-effect.html"),
("NIST-RESISTIVITY-HALL","https://www.nist.gov/pml/nanoscale-device-characterization-division/popular-links/hall-effect/resistivity-and-hall","nist-resistivity-hall.html"),
("NIST-DIELECTRIC-PERMITTIVITY-LOSS","https://www.nist.gov/publications/relative-permittivity-and-loss-tangent-measurement-using-nist-60-mm-cylindrical-cavity","nist-dielectric-permittivity-loss.html"),
("NIST-IONIC-CONDUCTIVITY","https://www.nist.gov/publications/low-temperature-ionic-conductivity-acceptor-doped-perovskite-part-i-impedance","nist-ionic-conductivity.html"),
("NIST-MIXED-IONIC-ELECTRONIC","https://www.nist.gov/node/1900911","nist-mixed-ionic-electronic.html"),
("NIST-TUNNEL-BAND-OFFSET","https://www.nist.gov/publications/electron-and-hole-photoemission-detection-band-offset-determination-tunnel-field-effect","nist-tunnel-band-offset.html"),
("NIST-OPTOELECTRONIC-BAND-METROLOGY","https://www.nist.gov/programs-projects/optical-and-optoelectronic-materials-characterization","nist-optoelectronic-band-metrology.html"),
("NIST-POINT-DEFECT-CHEMISTRY","https://www.nist.gov/programs-projects/measurements-point-defect-chemistry-complex-oxides","nist-point-defect-chemistry.html"),
("NIST-DIELECTRIC-DEPLETION","https://www.nist.gov/publications/electrical-conduction-and-dielectric-breakdown-aluminum-oxide-insulators-silicon","nist-dielectric-depletion.html"),
("NIST-OPERANDO-ELECTROCHEMICAL","https://www.nist.gov/programs-projects/operando-measurements-electrochemical-charge-transfer-processes","nist-operando-electrochemical.html"),)
def digest(b):return "sha256:"+sha256(b).hexdigest()
def canonical(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 rb=REG.read_bytes();reg=json.loads(rb)
 if reg["target_count"]!=12 or reg["target_content_present"] is not False:raise SystemExit("ELEC capture halted: registry changed")
 if OUT.exists():raise SystemExit("refusing to overwrite ELEC custody")
 OUT.mkdir(parents=True);docs=[]
 for sid,uri,name in REMOTE:
  with urlopen(Request(uri,headers={"User-Agent":"Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as response:body=response.read();status=getattr(response,"status",200);content=response.headers.get("Content-Type","unreported")
  if status!=200 or len(body)<1000:raise SystemExit(f"ELEC capture halted: {sid} {status} {len(body)}")
  path=OUT/name;path.write_bytes(body);docs.append({"source_id":sid,"source_uri":uri,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_hash":digest(body),"byte_count":len(body),"http_status":status,"content_type":content,"status":"captured_post_registry","used_for_favourable_comparison":True})
 registered={s for t in reg["targets"] for s in t["source_identities"]};captured={x["source_id"] for x in docs}
 if registered!=captured:raise SystemExit(f"ELEC source mismatch {registered-captured} {captured-registered}")
 p={"schema":"sft-v3-materials-elec-source-custody/1","target_registry_path":REG.relative_to(ROOT).as_posix(),"target_registry_hash":digest(rb),"target_registry_identity":reg["registry_identity"],"documents":docs,"document_count":len(docs),"captured_count":len(docs),"unavailable_count":0,"all_registered_source_identities_accounted_for":True,"all_result_classes_retained":True};p["manifest_identity"]=canonical(p);(OUT/"source_custody_manifest.json").write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"document_count":len(docs),"manifest_identity":p["manifest_identity"]},indent=2))
if __name__=="__main__":main()
