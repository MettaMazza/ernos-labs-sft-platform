#!/usr/bin/env python3
"""Capture the shared complete ECHEM-005–008 source family after four seals."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/external_sources/chemistry/snapshots/echem-005-008-transport-v1"
INVENTORY = OUT / "source-inventory-v1.json"

CLAIMS = (
    ("SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005", "experiments/external_sources/chemistry/echem_005_target_identities_v1.json", "sha256:a428b42998d2287c1432f7ccead2a41f10d17b6cf9426b2b0e5a59a6368981a7", "experiments/sealed_predictions/chemistry_echem_005_electrochemical_work_pre_source_v1.json", "sha256:935005aec0ea440426905e6b286330ec5244b66a1048d752d3976b9b6c443eac", "sha256:f574547a42bdf7c2cb3fa058193b52ce505b9fa7da49d7649ff5a0f6ddb2d5dd"),
    ("SFT-CHEM-ELECTROLYSIS-PRODUCT-AMOUNT-006", "experiments/external_sources/chemistry/echem_006_target_identities_v1.json", "sha256:0db005f92628714b58eb8d40156fc0aeff18dd0163ecad14ca900d8cfc51157c", "experiments/sealed_predictions/chemistry_echem_006_electrolysis_product_pre_source_v1.json", "sha256:f9552fd4768f68867e1519d9b6649e6c3cd028baa37f3cd1d64bcb2c357176e4", "sha256:98d1f9cdb46d04f28c874b1a7636ab056d62111fecc16466862c440460f47fae"),
    ("SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007", "experiments/external_sources/chemistry/echem_007_target_identities_v1.json", "sha256:a519269266aa9b5f136253657c3fc6f5409eaa884e2812b10b858b6597843574", "experiments/sealed_predictions/chemistry_echem_007_ionic_conductivity_pre_source_v1.json", "sha256:c950da3b805ff510084ec0c3d1b3f31ed79303e2a60d649e869130b34886154d", "sha256:9f471f13372f26a044b1c63633a61d878c81d2b1a6b62c15a4d81e14fdea977d"),
    ("SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008", "experiments/external_sources/chemistry/echem_008_target_identities_v1.json", "sha256:6f7a84294612efa2d3d9e4a7992310e4d8b4eb9e1d4c0c73dbe9927ea5eac35b", "experiments/sealed_predictions/chemistry_echem_008_ionic_mobility_transference_pre_source_v1.json", "sha256:59413d705ce5f3e962fd0723d46bf83ef0aba338cf9da62b5c598836da98b856", "sha256:039516f5097c6e83e6b937ab7004f031a835efd94ff4d858acb25f7a12a6ef01"),
)

SOURCES = (
    ("IUPAC-GREEN-BOOK-ELECTROCHEMISTRY-2007", "International Union of Pure and Applied Chemistry", "https://old.iupac.org/reports/provisional/abstract05/GreenBook051206_prs.pdf", "iupac-green-book-2007.pdf"),
    ("NIST-JRES-SILVER-ELECTROCHEMICAL-EQUIVALENT-1980", "National Bureau of Standards / National Institute of Standards and Technology", "https://nvlpubs.nist.gov/nistpubs/jres/85/jresv85n3p175_A1b.pdf", "nist-silver-electrochemical-equivalent-1980.pdf"),
    ("NIST-SP-260-176-SRM-CATALOG", "National Institute of Standards and Technology", "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.260-176.pdf", "nist-sp260-176-srm-catalog.pdf"),
    ("NIST-SP-260-142-PRIMARY-CONDUCTIVITY", "National Institute of Standards and Technology", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication260-142.pdf", "nist-sp260-142-primary-conductivity.pdf"),
    ("NIST-SRM-3190-CONDUCTIVITY-CERTIFICATE", "National Institute of Standards and Technology", "https://tsapps.nist.gov/srmext/certificates/archives/3190.pdf", "nist-srm-3190-certificate.pdf"),
    ("NBS-JRES-TRANSFERENCE-CONCENTRATION-1931", "National Bureau of Standards / National Institute of Standards and Technology", "https://nvlpubs.nist.gov/nistpubs/jres/6/jresv6n6p917_A2b.pdf", "nbs-transference-concentration-1931.pdf"),
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("ECHEM-005–008 capture already exists; recapture prohibited")
    sealed = []
    for claim_id, identity_path, identity_hash, seal_path, seal_hash, canonical_hash in CLAIMS:
        identity, seal = ROOT / identity_path, ROOT / seal_path
        if digest(identity.read_bytes()) != identity_hash or digest(seal.read_bytes()) != seal_hash:
            raise SystemExit(f"identity or seal changed for {claim_id}")
        payload = json.loads(seal.read_text()); recorded = payload.pop("sealed_payload_hash")
        reconstructed = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        if recorded != canonical_hash or reconstructed != canonical_hash:
            raise SystemExit(f"canonical pre-source seal invalid for {claim_id}")
        sealed.append({"claim_id": claim_id, "identity_sha256": identity_hash, "pre_source_seal_sha256": seal_hash, "canonical_payload_sha256": canonical_hash})
    OUT.mkdir(parents=True)
    rows = []
    for source_id, authority, uri, filename in SOURCES:
        with urlopen(Request(uri, headers={"User-Agent": "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"}), timeout=180) as response:
            payload, status, content_type = response.read(), response.status, response.headers.get("Content-Type")
        if status != 200 or not payload.startswith(b"%PDF"):
            raise SystemExit(f"complete source capture failed: {source_id}")
        path = OUT / filename; path.write_bytes(payload)
        rows.append({"source_id": source_id, "authority": authority, "uri": uri, "capture_status": "captured_once_after_all_four_claim_seals", "http_status": status, "content_type": content_type, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_bytes": len(payload), "snapshot_sha256": digest(payload)})
    inherited = (
        ("NIST-CODATA-2022-ALL-CONSTANTS", "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt", "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"),
        ("NIST-JRES-AGCL-STANDARD-POTENTIAL-1954", "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/nist-agcl-standard-potential-1954.pdf", "sha256:e1ebb99701a17746d9eb417938e435084c05d0cdaa50642279f54b706d2275ab"),
        ("NIST-JRES-AGCL-COMPLETE-POSTSEAL-ANALYSIS", "experiments/external_sources/chemistry/snapshots/echem-002-004-agcl-v1/complete-postseal-analysis-v2.json", "sha256:a6f1c117cfa3fe3f454dd5e86989d2105bc93586ca88370f0e4e541847088216"),
    )
    for source_id, path, expected in inherited:
        actual = digest((ROOT / path).read_bytes())
        if actual != expected:
            raise SystemExit(f"inherited source changed: {source_id}")
        rows.append({"source_id": source_id, "authority": "National Institute of Standards and Technology", "capture_status": "inherited_by_exact_hash_without_recapture", "snapshot_path": path, "snapshot_bytes": (ROOT / path).stat().st_size, "snapshot_sha256": actual})
    inventory = {"schema": "sft-v3-chemistry-echem-005-008-shared-source-inventory/1", "family_batch": "ECHEM-005-008", "all_four_claims_sealed_separately_before_new_sources_opened": True, "source_recapture_count": 0, "sealed_claims": sealed, "rows": rows}
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"inventory": INVENTORY.relative_to(ROOT).as_posix(), "inventory_sha256": digest(INVENTORY.read_bytes()), "sources": [{"source_id": row["source_id"], "sha256": row["snapshot_sha256"], "bytes": row["snapshot_bytes"]} for row in rows]}, indent=2))


if __name__ == "__main__":
    main()
