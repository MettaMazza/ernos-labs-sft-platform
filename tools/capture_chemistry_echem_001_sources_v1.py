#!/usr/bin/env python3
"""Capture complete ECHEM-001 sources once after its value-free seal."""
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];IDENTITY=ROOT/"experiments/external_sources/chemistry/echem_001_target_identities_v1.json";PRESEAL=ROOT/"experiments/sealed_predictions/chemistry_echem_001_half_reaction_pre_source_v1.json";OUT=ROOT/"experiments/external_sources/chemistry/snapshots/echem-001-half-reaction-v1";INVENTORY=OUT/"source-inventory-v1.json";EXPECTED_ID="sha256:c7d019931e60a60919942a344d48513ee599cb1c9dc9cdc7e83b14bfc53b9cf1";EXPECTED_SEAL="sha256:3172e99b46312d4f321cad4ab61747915388f74ef27789fe7623d0b882707a74";EXPECTED_PAYLOAD="sha256:1daf4589ba2281a1b2e147874920e28b1bc68b1beac3d85bc72c8231572c96da"
def digest(b):return "sha256:"+hashlib.sha256(b).hexdigest()
def fetch(uri):
 with urlopen(Request(uri,headers={"User-Agent":"Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"}),timeout=120) as r:return r.read(),r.status,dict(r.headers)
def main():
 if INVENTORY.exists():raise SystemExit("ECHEM-001 capture already exists; recapture prohibited")
 if digest(IDENTITY.read_bytes())!=EXPECTED_ID or digest(PRESEAL.read_bytes())!=EXPECTED_SEAL:raise SystemExit("ECHEM-001 identity or seal changed")
 d=json.loads(PRESEAL.read_text());claimed=d.pop("sealed_payload_hash")
 if claimed!=EXPECTED_PAYLOAD or digest(json.dumps(d,sort_keys=True,separators=(",",":")).encode())!=claimed:raise SystemExit("ECHEM-001 canonical seal invalid")
 OUT.mkdir(parents=True,exist_ok=True);rows=[]
 for source,name in zip(json.loads(IDENTITY.read_text())["sources"],("iupac-rt06783.json","nist-standard-electrode-potentials-1989.pdf")):
  payload,status,headers=fetch(source["uri"])
  if status!=200 or not payload:raise SystemExit(f"ECHEM-001 source failed: {source['source_id']}")
  path=OUT/name;path.write_bytes(payload);rows.append({**source,"capture_status":"captured_once_after_echem_001_seal","http_status":status,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_bytes":len(payload),"snapshot_sha256":digest(payload),"content_type":headers.get("Content-Type")})
 inv={"schema":"sft-v3-chemistry-echem-001-source-inventory/1","claim_id":"SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001","identity_sha256":EXPECTED_ID,"pre_source_seal_sha256":EXPECTED_SEAL,"source_recapture_count":0,"all_sources_opened_only_after_claim_seal":True,"rows":rows};INVENTORY.write_text(json.dumps(inv,indent=2,sort_keys=True)+"\n");print(json.dumps({"inventory":INVENTORY.relative_to(ROOT).as_posix(),"inventory_sha256":digest(INVENTORY.read_bytes()),"sources":rows},indent=2))
if __name__=="__main__":main()
