#!/usr/bin/env python3
"""Freeze the linked OPT-003 quantum-yield source before opening its document."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "census/materials_opt_001_010_target_registry_v1.json"
OUT = ROOT / "census/materials_opt_003_quantum_yield_source_addendum_v1.json"

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    base = json.loads(BASE.read_text())
    if base["registry_identity"] != "sha256:f0e4c811c7871b07a57973b232ff78269797c37894af88cab83cc59ec52e4a77" or base["target_content_present"] is not False:
        raise SystemExit("OPT base registry changed")
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    payload = {
        "schema": "sft-v3-materials-opt-source-addendum/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "base_target_registry_identity": base["registry_identity"],
        "obligation_id": "SFT-MAT-OBL-OPT-003",
        "claim_id": "SFT-MAT-OPT-LUMINESCENCE-YIELD-003",
        "reason": "The initially registered fluorescence/Raman calibration programme establishes absolute signal custody but does not expose the complete quantum-yield relation in the captured programme page; the limitation is preserved and the linked NIST calibration guide is registered before opening.",
        "source_id": "NIST-FLUORESCENCE-QUANTUM-YIELD-GUIDE",
        "source_uri": "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7458.pdf",
        "target_class": "emitted-photon to absorbed-photon quantum-yield relation with specified measurement conditions",
        "target_content_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "survivor_identity_present": False,
        "failed_initial_source_hidden": False,
    }
    payload["addendum_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(payload["addendum_identity"])

if __name__ == "__main__":
    main()
