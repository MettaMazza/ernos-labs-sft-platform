#!/usr/bin/env python3
"""Seal the post-law ANAL-001 certificate-source addendum before capture."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IDENTITY=ROOT/"experiments/external_sources/chemistry/anal_001_srm1959_certificate_addendum_identity_v1.json"
LAW_SEAL=ROOT/"experiments/sealed_predictions/chemistry_anal_001_pre_source_v1.json"
OUTPUT=ROOT/"experiments/sealed_predictions/chemistry_anal_001_certificate_addendum_pre_capture_v1.json"
def digest(data): return "sha256:"+hashlib.sha256(data).hexdigest()
def main():
 if OUTPUT.exists(): raise SystemExit("ANAL-001 certificate addendum seal exists; replacement prohibited")
 if digest(IDENTITY.read_bytes())!="sha256:1ece632f292fa382e3c3e027f0c5f40ddf593519e864241f4576f033f6ddc35c": raise SystemExit("ANAL-001 addendum identity changed")
 if digest(LAW_SEAL.read_bytes())!="sha256:955ded74c39ffa1ab805b5cbe462c6c02768acf1101b2946708df85ac438ed03": raise SystemExit("ANAL-001 native law seal changed")
 payload={"schema":"sft-v3-post-law-source-addendum-seal/1","claim_id":"SFT-CHEM-ANALYTICAL-ACCURACY-TRUENESS-001","sealed_date":"2026-07-28","native_law_seal_hash":"sha256:955ded74c39ffa1ab805b5cbe462c6c02768acf1101b2946708df85ac438ed03","source_addendum_identity_path":IDENTITY.relative_to(ROOT).as_posix(),"source_addendum_identity_hash":digest(IDENTITY.read_bytes()),"complete_certificate_captured_before_addendum_seal":False,"disclosed_search_snippets_never_relabelled_blind":True,"source_value_or_outcome_allowed_to_change_native_law_or_survivor":False}
 payload["sealed_payload_hash"]=digest(json.dumps(payload,sort_keys=True,separators=(",",":")).encode());OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(digest(OUTPUT.read_bytes()),payload["sealed_payload_hash"])
if __name__=="__main__": main()
