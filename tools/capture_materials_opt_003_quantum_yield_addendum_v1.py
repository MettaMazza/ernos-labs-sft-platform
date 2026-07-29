#!/usr/bin/env python3
"""Capture the pre-registered linked OPT-003 NIST quantum-yield guide."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_opt_003_quantum_yield_source_addendum_v1.json"
OUT = ROOT / "experiments/external_sources/materials/opt_001_010_v1/opt_003_quantum_yield_source_addendum_v1.json"

def digest(data):
    return "sha256:" + sha256(data).hexdigest()

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_content_present"] is not False or registry["source_id"] != "NIST-FLUORESCENCE-QUANTUM-YIELD-GUIDE":
        raise SystemExit("OPT-003 addendum registry changed")
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    with urlopen(Request(registry["source_uri"], headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}), timeout=120) as response:
        body = response.read()
        status = getattr(response, "status", 200)
        content_type = response.headers.get("Content-Type", "unreported")
    if status != 200 or len(body) < 10000:
        raise SystemExit(f"OPT-003 addendum capture halt {status} {len(body)}")
    snapshot = OUT.parent / "nistir7458-fluorescence-quantum-yield.pdf"
    snapshot.write_bytes(body)
    payload = {
        "schema": "sft-v3-materials-opt-source-addendum-custody/1",
        "source_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "source_registry_hash": digest(registry_bytes),
        "source_registry_identity": registry["addendum_identity"],
        "base_target_registry_identity": registry["base_target_registry_identity"],
        "source_id": registry["source_id"],
        "source_uri": registry["source_uri"],
        "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
        "snapshot_hash": digest(body),
        "byte_count": len(body),
        "http_status": status,
        "content_type": content_type,
        "status": "captured_post_addendum_registry",
        "initial_source_limitation_preserved": True,
    }
    payload["manifest_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"bytes": len(body), "identity": payload["manifest_identity"]}, indent=2))

if __name__ == "__main__":
    main()
