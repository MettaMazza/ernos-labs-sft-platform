#!/usr/bin/env python3
"""Capture the preregistered ORG-011 Claisen supplement exactly once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_011_target_identities_v2.json"
IDENTITY_HASH = "sha256:80580233b667e2350ee29f05a86dc03292d249ebac0cbffac27b987bc8939d34"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_011_rearrangement_reaction_pre_source_v2.json"
PRESEAL_HASH = "sha256:6808f37f9cf1faa657e5f5a5c65483f6b8585aa35bd0fd229774165ed1691c7c"
PRESEAL_PAYLOAD_HASH = "sha256:a772e044a114e8cea5d8698148f46ffe8d6b4f0165eb976b3513eb2245bed36e"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2"
REGISTERED_FILENAME = "NIHMS54435-supplement-1.pdf"
PMC_URI = "https://pmc.ncbi.nlm.nih.gov/articles/instance/2547484/bin/NIHMS54435-supplement-1.pdf"
PUBLISHER_RECORD_DOI = "10.1021/ja803370x.s001"
PUBLISHER_API_URI = "https://api.figshare.com/v2/articles/2925988"
PUBLISHER_DOWNLOAD_URI = "https://ndownloader.figshare.com/files/4624453"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    if digest_file(IDENTITY) != IDENTITY_HASH or digest_file(PRESEAL) != PRESEAL_HASH:
        raise SystemExit("ORG-011 V2 identity or prediction seal changed")
    seal = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash")
    if claimed != PRESEAL_PAYLOAD_HASH or sha256_identity(seal) != PRESEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-011 V2 canonical prediction seal changed")
    if OUTPUT.exists():
        raise SystemExit("ORG-011 V2 source already captured; recapture prohibited")

    rejected_request = urllib.request.Request(
        PMC_URI,
        headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"},
    )
    with urllib.request.urlopen(rejected_request, timeout=120) as response:
        rejected_payload = response.read()
        rejected_status = response.status
        rejected_content_type = response.headers.get("Content-Type", "")
    if rejected_payload.startswith(b"%PDF"):
        raise SystemExit("ORG-011 registered PMC transport unexpectedly changed; review before capture")

    api_request = urllib.request.Request(
        PUBLISHER_API_URI,
        headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"},
    )
    with urllib.request.urlopen(api_request, timeout=120) as response:
        publisher_record_payload = response.read()
        publisher_record_status = response.status
    publisher_record = json.loads(publisher_record_payload.decode("utf-8"))
    files = tuple(publisher_record.get("files", ()))
    if (
        publisher_record_status != 200
        or publisher_record.get("doi") != PUBLISHER_RECORD_DOI
        or len(files) != 1
        or files[0].get("id") != 4624453
        or files[0].get("name") != "ja803370x_si_001.pdf"
        or files[0].get("download_url") != PUBLISHER_DOWNLOAD_URI
    ):
        raise SystemExit("ORG-011 official ACS Figshare supplement identity changed")

    request = urllib.request.Request(
        PUBLISHER_DOWNLOAD_URI,
        headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
        headers = dict(response.headers.items())
        status = response.status
        final_uri = response.geturl()
    if status != 200 or not payload.startswith(b"%PDF"):
        raise SystemExit("ORG-011 V2 supplementary PDF capture failed")

    OUTPUT.mkdir(parents=True)
    path = OUTPUT / files[0]["name"]
    path.write_bytes(payload)
    publisher_record_path = OUTPUT / "acs-figshare-s001-record-v2.json"
    publisher_record_path.write_bytes(publisher_record_payload)
    inventory = {
        "schema": "sft-v3-chemistry-org-011-claisen-source-inventory/2",
        "claim_id": "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011",
        "capture_status": "captured_once_after_claim_specific_v2_seal",
        "source_recapture_count": 0,
        "registered_pmc_uri": PMC_URI,
        "registered_pmc_filename": REGISTERED_FILENAME,
        "registered_pmc_transport_attempt": {
            "http_status": rejected_status,
            "content_type": rejected_content_type,
            "payload_bytes": len(rejected_payload),
            "payload_sha256": digest_bytes(rejected_payload),
            "result": "rejected_non_pdf_recaptcha_transport",
        },
        "publisher_record_doi": PUBLISHER_RECORD_DOI,
        "publisher_api_uri": PUBLISHER_API_URI,
        "publisher_record_path": publisher_record_path.relative_to(ROOT).as_posix(),
        "publisher_record_bytes": len(publisher_record_payload),
        "publisher_record_sha256": digest_bytes(publisher_record_payload),
        "publisher_download_uri": PUBLISHER_DOWNLOAD_URI,
        "final_uri": final_uri,
        "http_status": status,
        "response_headers": headers,
        "snapshot_path": path.relative_to(ROOT).as_posix(),
        "snapshot_bytes": len(payload),
        "snapshot_sha256": digest_bytes(payload),
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": PRESEAL_HASH,
        "target_identity_path": IDENTITY.relative_to(ROOT).as_posix(),
        "target_identity_sha256": IDENTITY_HASH,
    }
    inventory_path = OUTPUT / "source-inventory-v2.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "snapshot_bytes": len(payload),
                "snapshot_sha256": inventory["snapshot_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
