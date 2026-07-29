#!/usr/bin/env python3
"""Strip the frozen VALID evidence vector to a value-free dependency registry."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"experiments/external_sources/chemistry/valid_001_012_complete_empirical_vector_v2.json"
OUTPUT=ROOT/"census/chemistry_valid_001_012_dependency_registry_v2.json"
def ident(x):return "sha256:"+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 if OUTPUT.exists():raise SystemExit("VALID dependency registry already exists; freeze preserved")
 source=json.loads(SOURCE.read_text());payload={"schema":"sft-v3-chemistry-valid-dependency-registry/2","date":"2026-07-29","scope":"value-free identities and dependency memberships only; no measurement line, observed value, comparison result or survivor content","evidence_vector_file_hash":"sha256:"+hashlib.sha256(SOURCE.read_bytes()).hexdigest(),"evidence_vector_identity":source["complete_vector_identity"],"vector_claim_ids":source["vector_claim_ids"],"vector_claim_counts":source["vector_claim_counts"],"target_content_present":False};payload["registry_identity"]=ident(payload);OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"output":OUTPUT.relative_to(ROOT).as_posix(),"registry_identity":payload["registry_identity"],"counts":payload["vector_claim_counts"]},indent=2))
if __name__=="__main__":main()
