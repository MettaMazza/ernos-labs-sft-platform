#!/usr/bin/env python3
"""Capture the preregistered ORG-010 supplementary archive exactly once."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_010_target_identities_v1.json"
IDENTITY_HASH = "sha256:fffd58022997ba69d30e1cd940fc600465b39d9a7c4cfab993b1799c3302cefe"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_010_elimination_reaction_pre_source_v1.json"
PRESEAL_HASH = "sha256:13869cd3759eea606af331d1aa8468c77f3b1449c41c6c0ac52db757bd702239"
PRESEAL_PAYLOAD_HASH = "sha256:c0a9be98e698ea18317d3cf66f431f56c11e38f78d5bb835f4eb4562d9d08c39"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
ARCHIVE_NAME = "PMC11186341_SupplementaryFiles.zip"
URI = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11186341/supplementaryFiles"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    if digest_file(IDENTITY) != IDENTITY_HASH or digest_file(PRESEAL) != PRESEAL_HASH:
        raise SystemExit("ORG-010 identity or prediction seal changed")
    seal = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash")
    if claimed != PRESEAL_PAYLOAD_HASH or sha256_identity(seal) != PRESEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-010 canonical prediction seal changed")
    if OUTPUT.exists():
        raise SystemExit("ORG-010 source already captured; recapture prohibited")

    request = urllib.request.Request(URI, headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
        headers = dict(response.headers.items())
        status = response.status
    if status != 200 or not payload.startswith(b"PK"):
        raise SystemExit("ORG-010 supplementary archive capture failed")

    archive = zipfile.ZipFile(io.BytesIO(payload))
    members = tuple(info for info in archive.infolist() if not info.is_dir())
    if not members or not any(info.filename.endswith("SC-015-D4SC01905A-s001.pdf") for info in members):
        raise SystemExit("ORG-010 registered supplementary PDF is absent")
    OUTPUT.mkdir(parents=True)
    archive_path = OUTPUT / ARCHIVE_NAME
    archive_path.write_bytes(payload)
    member_rows = []
    for info in members:
        name = Path(info.filename).name
        if name != info.filename or not name:
            raise SystemExit("ORG-010 archive contains an unsafe member path")
        content = archive.read(info)
        path = OUTPUT / name
        path.write_bytes(content)
        member_rows.append({
            "archive_member": info.filename,
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_bytes": len(content),
            "snapshot_sha256": digest_bytes(content),
        })
    inventory = {
        "schema": "sft-v3-chemistry-org-010-source-inventory/1",
        "claim_id": "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010",
        "capture_status": "captured_once_after_claim_specific_seal",
        "source_recapture_count": 0,
        "uri": URI,
        "http_status": status,
        "response_headers": headers,
        "archive_path": archive_path.relative_to(ROOT).as_posix(),
        "archive_bytes": len(payload),
        "archive_sha256": digest_bytes(payload),
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": PRESEAL_HASH,
        "members": member_rows,
    }
    (OUTPUT / "source-inventory-v1.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "archive_sha256": inventory["archive_sha256"],
        "archive_bytes": inventory["archive_bytes"],
        "member_count": len(member_rows),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
