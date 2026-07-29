#!/usr/bin/env python3
"""Capture the NUCHEM-001–004 source family once after all four seals."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1";INV=OUT/"source-inventory-v1.json"
SOURCES=(
("NIST-RADIOACTIVITY-SRMS-GENERAL-INFO-2025","https://tsapps.nist.gov/srmext/certificates/documents/Radioactivity%20SRMs%20General%20Info.pdf","nist-radioactivity-srms-general-info-2025.pdf"),
("NIST-SRM-4239A-STRONTIUM-90-2022","https://tsapps.nist.gov/srmext/certificates/4239a.pdf","nist-srm-4239a-strontium-90.pdf"),
("NIST-SRM-4324C-URANIUM-232-2025","https://www.nist.gov/programs-projects/standard-reference-materials-standardization-232u-srm-4324c","nist-srm-4324c-uranium-232.html"),
("NIST-NUCLEAR-PHYSICS-DATA-ISOTOPIC-COMPOSITION","https://www.nist.gov/pml/nuclear-physics-data","nist-nuclear-physics-data.html"))
SEALS=(("001","sha256:e6a292d3ea5d8b3afe46e66d65bcdfae056ea40c508ee0bd787794c562bc7104"),("002","sha256:3c3ede4d5d1f516a99e364b51e9462dd86214f5b640ee0008da3558102e39454"),("003","sha256:c16ac68db0ccb2c18515a007a756eac46595b8cbebe6078a1e16be23572ff9d3"),("004","sha256:3c03263c9c780e0888d90e0a4519726640dd9eb9f8ed1084bbc85ed590861ae0"))
def h(b):return "sha256:"+hashlib.sha256(b).hexdigest()
def main():
 if INV.exists():raise SystemExit("NUCHEM source capture already exists")
 for n,x in SEALS:
  p=ROOT/f"experiments/sealed_predictions/chemistry_nuchem_{n}_pre_source_v1.json"
  if h(p.read_bytes())!=x:raise SystemExit(f"seal changed {n}")
 OUT.mkdir(parents=True,exist_ok=False);rows=[]
 for sid,url,name in SOURCES:
  req=urllib.request.Request(url,headers={"User-Agent":"Ernos-Labs-SFT/3 source-custody Maria.Smith.Sftoe@gmail.com"});data=urllib.request.urlopen(req,timeout=60).read();(OUT/name).write_bytes(data);rows.append({"source_id":sid,"authority":"National Institute of Standards and Technology","uri":url,"snapshot_path":(OUT/name).relative_to(ROOT).as_posix(),"snapshot_sha256":h(data),"snapshot_bytes":len(data),"capture_status":"captured_once_after_all_four_claim_seals"})
 p={"schema":"sft-v3-chemistry-nuchem-001-004-source-inventory/1","family":"NUCHEM-001-004","all_four_claims_sealed_separately_before_source_capture":True,"sealed_claims":[{"claim":n,"seal_sha256":x} for n,x in SEALS],"rows":rows};INV.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"inventory":INV.relative_to(ROOT).as_posix(),"inventory_sha256":h(INV.read_bytes()),"sources":len(rows),"bytes":sum(x["snapshot_bytes"] for x in rows)},indent=2))
if __name__=="__main__":main()
