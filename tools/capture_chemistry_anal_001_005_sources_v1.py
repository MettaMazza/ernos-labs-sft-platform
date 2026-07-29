#!/usr/bin/env python3
"""Capture complete ANAL-001–005 sources once after all five seals."""
import hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/"experiments/external_sources/chemistry/snapshots/anal-001-005-performance-v1"
INVENTORY=SNAP/"source-inventory-v1.json"
REGISTRY=ROOT/"experiments/external_sources/chemistry/anal_001_005_family_source_identity_registry_v1.json"
EXPECTED_REGISTRY="sha256:2752bc157bb4529bff6c2c73b96671516e814c12e895ac48758730a2802e7109"
SOURCES=(
 ("NIST-SRM-1959-CERTIFICATION-2010","National Institute of Standards and Technology","https://www.nist.gov/publications/certification-drugs-abuse-human-serum-standard-reference-material-srm-1959","nist-srm1959-certification-page.html","html"),
 ("NIST-SP-260-126-NTRM-GAS-STANDARDS","National Institute of Standards and Technology","https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication260-126.pdf","nist-sp260-126-ntrm-gas-standards.pdf","pdf"),
 ("NIST-SP958-DETECTION-QUANTIFICATION-PAGES-164-166","National Institute of Standards and Technology","https://nvlpubs.nist.gov/nistpubs/sp958-lide/164-166.pdf","nist-sp958-detection-quantification-164-166.pdf","pdf"),
 ("IUPAC-PAC-2001-SELECTIVITY","International Union of Pure and Applied Chemistry","https://publications.iupac.org/publications/pac/2001/pdf/7308x1381.pdf","iupac-selectivity-2001.pdf","pdf"),
 ("NIST-IMS-FENTANYL-INTERFERENTS-2019","National Institute of Standards and Technology","https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=927862","nist-ims-fentanyl-interferents-2019.pdf","pdf"),)
SEALS={
 "001":("experiments/sealed_predictions/chemistry_anal_001_pre_source_v1.json","sha256:955ded74c39ffa1ab805b5cbe462c6c02768acf1101b2946708df85ac438ed03"),
 "002":("experiments/sealed_predictions/chemistry_anal_002_pre_source_v1.json","sha256:9d7fa5db0e6cc0f3f8485e92bbe9e1e33722dd08743d0fafbf7796ed01003d14"),
 "003":("experiments/sealed_predictions/chemistry_anal_003_pre_source_v1.json","sha256:293d37ff1ab266cb7636f06115c87213d392cfd6a6d7341d6f222c96c73b91ff"),
 "004":("experiments/sealed_predictions/chemistry_anal_004_pre_source_v1.json","sha256:9355f073f2f0312d66f9172873199a91ec22b5a82bef7b68d7c01ffe7c7d4be1"),
 "005":("experiments/sealed_predictions/chemistry_anal_005_pre_source_v1.json","sha256:41f0a6127c39b4dd820d8d1ac3e5bb47fd69fd45068ff04f0e5f316eaa9b204f"),}
def digest(data): return "sha256:"+hashlib.sha256(data).hexdigest()
def main():
 if INVENTORY.exists(): raise SystemExit("ANAL-001–005 source inventory already exists; recapture prohibited")
 if digest(REGISTRY.read_bytes())!=EXPECTED_REGISTRY: raise SystemExit("ANAL-001–005 registry changed")
 for key,(path,expected) in SEALS.items():
  if digest((ROOT/path).read_bytes())!=expected: raise SystemExit(f"ANAL-{key} seal changed")
 SNAP.mkdir(parents=True,exist_ok=False);rows=[]
 for source_id,authority,uri,name,kind in SOURCES:
  with urlopen(Request(uri,headers={"User-Agent":"Ernos-Labs-SFT-Empirical-Capture/1.0"}),timeout=120) as response: payload=response.read();content_type=response.headers.get("Content-Type","")
  if kind=="pdf" and not payload.startswith(b"%PDF-"): raise SystemExit(f"registered PDF source changed transport: {source_id}")
  if kind=="html" and b"SRM 1959" not in payload: raise SystemExit(f"registered HTML source changed content: {source_id}")
  path=SNAP/name;path.write_bytes(payload);rows.append({"source_id":source_id,"authority":authority,"uri":uri,"capture_status":"captured_once_after_all_five_claim_seals","media_kind":kind,"content_type":content_type,"snapshot_path":path.relative_to(ROOT).as_posix(),"snapshot_sha256":digest(payload),"snapshot_bytes":len(payload)});print(source_id,len(payload),digest(payload))
 inventory={"schema":"sft-v3-chemistry-anal-001-005-source-inventory/1","family":"ANAL-001-005","all_five_claims_sealed_separately_before_complete_family_capture":True,"prior_source_exposure_disclosures_preserved_in_each_seal":True,"sealed_claims":[{"claim":k,"seal_sha256":x} for k,(_,x) in SEALS.items()],"rows":rows}
 INVENTORY.write_text(json.dumps(inventory,indent=2,sort_keys=True)+"\n");print("inventory",digest(INVENTORY.read_bytes()))
if __name__=="__main__": main()
