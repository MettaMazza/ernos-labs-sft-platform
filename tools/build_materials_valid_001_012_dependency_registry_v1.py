#!/usr/bin/env python3
"""Strip the frozen Materials VALID evidence vector to value-free memberships."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SOURCE=ROOT/"experiments/external_sources/materials/valid_001_012_complete_empirical_vector_v1.json"; OUT=ROOT/"census/materials_valid_001_012_dependency_registry_v1.json"
def ident(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists(): raise SystemExit("Materials VALID registry already frozen")
 source=json.loads(SOURCE.read_text()); v={"schema":"sft-v3-materials-valid-dependency-registry/1","date":"2026-07-29","scope":"value-free identities and memberships only; no measurement line, observed value, result or survivor content","evidence_vector_file_hash":"sha256:"+sha256(SOURCE.read_bytes()).hexdigest(),"evidence_vector_identity":source["complete_vector_identity"],"vector_claim_ids":source["vector_claim_ids"],"vector_claim_counts":source["vector_claim_counts"],"target_content_present":False}; v["registry_identity"]=ident(v); OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n"); print(json.dumps({"identity":v["registry_identity"],"counts":v["vector_claim_counts"]},indent=2))
if __name__=="__main__": main()
