#!/usr/bin/env python3
"""Capture the sealed ANAL-001 SRM 1959 certificate addendum once."""
import hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/"experiments/external_sources/chemistry/snapshots/anal-001-005-performance-v1"
OUTPUT=SNAP/"anal-001-srm1959-certificate-addendum-inventory-v1.json"
PDF=SNAP/"nist-srm1959-certificate-2011.pdf"
IDENTITY=ROOT/"experiments/external_sources/chemistry/anal_001_srm1959_certificate_addendum_identity_v1.json"
SEAL=ROOT/"experiments/sealed_predictions/chemistry_anal_001_certificate_addendum_pre_capture_v1.json"
URL="https://tsapps.nist.gov/srmext/certificates/archives/1959.pdf"
def digest(data): return "sha256:"+hashlib.sha256(data).hexdigest()
def main():
 if OUTPUT.exists() or PDF.exists(): raise SystemExit("ANAL-001 certificate addendum already captured; replacement prohibited")
 if digest(IDENTITY.read_bytes())!="sha256:1ece632f292fa382e3c3e027f0c5f40ddf593519e864241f4576f033f6ddc35c" or digest(SEAL.read_bytes())!="sha256:e75404075f3f90b264d929207d63026b0accd26ebfe9271d060ec1a58df2d4ae": raise SystemExit("ANAL-001 certificate addendum identity or seal changed")
 with urlopen(Request(URL,headers={"User-Agent":"Ernos-Labs-SFT-Empirical-Capture/1.0"}),timeout=120) as response: payload=response.read();content_type=response.headers.get("Content-Type","")
 if not payload.startswith(b"%PDF-"): raise SystemExit("ANAL-001 certificate transport was not PDF")
 PDF.write_bytes(payload);record={"schema":"sft-v3-post-law-source-addendum-capture/1","claim_id":"SFT-CHEM-ANALYTICAL-ACCURACY-TRUENESS-001","source_id":"NIST-SRM-1959-CERTIFICATE-2011","uri":URL,"content_type":content_type,"snapshot_path":PDF.relative_to(ROOT).as_posix(),"snapshot_sha256":digest(payload),"snapshot_bytes":len(payload),"captured_once_after_addendum_seal":True,"native_law_or_survivor_changed":False};OUTPUT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n");print(len(payload),digest(payload),digest(OUTPUT.read_bytes()))
if __name__=="__main__": main()
