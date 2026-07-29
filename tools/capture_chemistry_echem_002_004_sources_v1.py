#!/usr/bin/env python3
"""Capture the one shared complete NIST source after three separate claim seals."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1"
PDF = OUT / "nist-agcl-standard-potential-1954.pdf"
INVENTORY = OUT / "source-inventory-v1.json"
URI = "https://nvlpubs.nist.gov/nistpubs/jres/53/jresv53n5p283_a1b.pdf"
CLAIMS = (
    ("SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002", "experiments/external_sources/chemistry/echem_002_target_identities_v1.json", "sha256:a2b0c83ce705aeff8bb20371446f27acc5b59e52d8e727698f4a37cbee325fb9", "experiments/sealed_predictions/chemistry_echem_002_electrode_potential_pre_source_v1.json", "sha256:57199514491854ce54165ae100ba7008c0bbd03ac304259aa50e7dccbc3b949f", "sha256:34c31c791198560e132cd5d2d48dbcd7dc688b11a2192b461cc28df615fbf36b"),
    ("SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003", "experiments/external_sources/chemistry/echem_003_target_identities_v1.json", "sha256:94bfdfcfa5920a285c555c541aecd1e678b92848c06e11305f9bd3a894131e45", "experiments/sealed_predictions/chemistry_echem_003_cell_potential_pre_source_v1.json", "sha256:b87a3450fd9a9596f5f410747fdb223ec8e88005ed1173f965aeee422a3d1a83", "sha256:6613f5bd3fbcd755149c55fb342b7d7ee1114476300590645a8a59adb24f471f"),
    ("SFT-CHEM-CONCENTRATION-DEPENDENT-POTENTIAL-004", "experiments/external_sources/chemistry/echem_004_target_identities_v1.json", "sha256:30b9bd6af83114eca87e914f888c412d1d540bca731b97dc335daccd7c75c174", "experiments/sealed_predictions/chemistry_echem_004_concentration_potential_pre_source_v1.json", "sha256:87df635946459c70aa7c7defec2c2af105096838179d846524c8320f861bad39", "sha256:2f32250f79ff8283a361ef231fb61b69532b7b7fd0b9f5132b16c21251f11542"),
)

def digest(payload):
    return "sha256:" + hashlib.sha256(payload).hexdigest()

def main():
    if INVENTORY.exists() or PDF.exists():
        raise SystemExit("ECHEM-002-004 shared capture already exists; recapture prohibited")
    sealed_claims = []
    for claim_id, identity_path, identity_hash, seal_path, seal_hash, payload_hash in CLAIMS:
        identity = ROOT / identity_path
        seal = ROOT / seal_path
        if digest(identity.read_bytes()) != identity_hash or digest(seal.read_bytes()) != seal_hash:
            raise SystemExit(f"identity or seal changed for {claim_id}")
        document = json.loads(seal.read_text())
        recorded = document.pop("sealed_payload_hash")
        canonical = digest(json.dumps(document, sort_keys=True, separators=(",", ":")).encode())
        if recorded != payload_hash or canonical != payload_hash:
            raise SystemExit(f"canonical pre-source seal invalid for {claim_id}")
        sealed_claims.append({"claim_id": claim_id, "identity_sha256": identity_hash, "pre_source_seal_sha256": seal_hash, "canonical_payload_sha256": payload_hash})
    with urlopen(Request(URI, headers={"User-Agent": "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"}), timeout=120) as response:
        payload, status, content_type = response.read(), response.status, response.headers.get("Content-Type")
    if status != 200 or not payload.startswith(b"%PDF"):
        raise SystemExit("complete NIST Ag/AgCl PDF capture failed")
    OUT.mkdir(parents=True, exist_ok=True)
    PDF.write_bytes(payload)
    inventory = {
        "schema": "sft-v3-chemistry-echem-002-004-shared-source-inventory/1",
        "family_batch": "ECHEM-002-004",
        "all_three_claims_sealed_separately_before_source_opened": True,
        "source_recapture_count": 0,
        "sealed_claims": sealed_claims,
        "rows": [{
            "source_id": "NIST-JRES-AGCL-STANDARD-POTENTIAL-1954",
            "authority": "National Bureau of Standards / National Institute of Standards and Technology",
            "uri": URI,
            "capture_status": "captured_once_after_all_three_claim_seals",
            "http_status": status,
            "content_type": content_type,
            "snapshot_path": PDF.relative_to(ROOT).as_posix(),
            "snapshot_bytes": len(payload),
            "snapshot_sha256": digest(payload),
        }],
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"inventory": INVENTORY.relative_to(ROOT).as_posix(), "inventory_sha256": digest(INVENTORY.read_bytes()), "pdf_sha256": digest(payload), "pdf_bytes": len(payload)}, indent=2))

if __name__ == "__main__":
    main()
