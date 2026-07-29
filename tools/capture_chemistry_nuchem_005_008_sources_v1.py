#!/usr/bin/env python3
"""Capture NUCHEM-005–008 sources once after all four separate seals."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-005-008-isotope-v1"
INVENTORY = OUT / "source-inventory-v1.json"
SEALS = (
    ("005", "sha256:9436a1000ff1efdf8b2f934f9f44024e5fd8862da321ab2182f96fccd0d95a91"),
    ("006", "sha256:bcd18bde92a7ee35b3541a0d83ed3ac3cb54c323dd26482d7d3f1bf76f7ea5f8"),
    ("007", "sha256:0733d1926431ed8e6f875f13f9fa6a81eee6b509e565c97f5d4491ad6d891944"),
    ("008", "sha256:938778dff4ddcc3896f0e4e3be91c878fa346bca3fe51f63f3a8b2c0ae53af1a"),
)
REUSED = (
    ("NIST-SRM-4239A-STRONTIUM-90-2022", "National Institute of Standards and Technology", "https://tsapps.nist.gov/srmext/certificates/4239a.pdf", "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/nist-srm-4239a-strontium-90.pdf", "sha256:e8f3f5397db147ce57a270c25e4fd655ca6bacc5b8e6652e3a3df57c36ea346e"),
    ("NIST-SRM-4324C-URANIUM-232-2025", "National Institute of Standards and Technology", "https://www.nist.gov/programs-projects/standard-reference-materials-standardization-232u-srm-4324c", "experiments/external_sources/chemistry/snapshots/nuchem-001-004-radioactivity-v1/nist-srm-4324c-uranium-232.html", "sha256:ab8ce95a445b7c665187d5d347ff57fa06e94082aa9177c09ec2df8c77433a23"),
)
DOWNLOADS = (
    ("USGS-WRIR-02-4172-ISOTOPE-EQUILIBRIUM-CONSTANTS", "United States Geological Survey", "https://pubs.usgs.gov/wri/wrir02-4172/pdf/wrir02-4172.pdf", "usgs-wrir02-4172-isotope-equilibrium.pdf"),
    ("USGS-PP-440-KK-STABLE-ISOTOPE-FRACTIONATION", "United States Geological Survey", "https://pubs.usgs.gov/pp/0440kk/report.pdf", "usgs-pp440kk-stable-isotope-fractionation.pdf"),
    ("NBS-RP729-ELECTROLYTIC-HYDROGEN-OXYGEN-FRACTIONATION-1934", "National Bureau of Standards", "https://nvlpubs.nist.gov/nistpubs/jres/13/jresv13n5p599_A2b.pdf", "nbs-rp729-electrolytic-isotope-fractionation-1934.pdf"),
)


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("NUCHEM-005–008 capture exists")
    sealed = []
    for number, expected in SEALS:
        path = ROOT / f"experiments/sealed_predictions/chemistry_nuchem_{number}_pre_source_v1.json"
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"seal changed {number}")
        sealed.append({"claim": number, "seal_sha256": expected})
    OUT.mkdir(parents=True)
    rows = []
    for source_id, authority, uri, relative, expected in REUSED:
        path = ROOT / relative
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"reused source changed {source_id}")
        rows.append({"source_id": source_id, "authority": authority, "uri": uri, "snapshot_path": relative, "snapshot_sha256": expected, "snapshot_bytes": path.stat().st_size, "capture_status": "exact_hash_reuse_from_postseal_NUCHEM_001_004_capture__not_recaptured"})
    for source_id, authority, uri, name in DOWNLOADS:
        request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT/3 source-custody Maria.Smith.Sftoe@gmail.com"})
        with urlopen(request, timeout=180) as response:
            data, status, content_type = response.read(), response.status, response.headers.get("Content-Type")
        if status != 200 or not data.startswith(b"%PDF"):
            raise SystemExit(f"capture failed {source_id}")
        path = OUT / name; path.write_bytes(data)
        rows.append({"source_id": source_id, "authority": authority, "uri": uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_sha256": digest(data), "snapshot_bytes": len(data), "content_type": content_type, "capture_status": "captured_once_after_all_four_claim_seals"})
    inventory = {
        "schema": "sft-v3-chemistry-nuchem-005-008-source-inventory/1", "family": "NUCHEM-005-008",
        "all_four_claims_sealed_separately_before_complete_family_capture": True,
        "prior_source_exposure_disclosures_preserved_in_each_seal": True,
        "sealed_claims": sealed, "rows": rows,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"inventory": INVENTORY.relative_to(ROOT).as_posix(), "inventory_sha256": digest(INVENTORY.read_bytes()), "source_rows": len(rows), "new_captures": len(DOWNLOADS), "exact_reuses": len(REUSED), "total_bytes": sum(row["snapshot_bytes"] for row in rows)}, indent=2))


if __name__ == "__main__":
    main()
