#!/usr/bin/env python3
"""Capture the preregistered ORG-011 supplementary archive exactly once."""

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


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_011_target_identities_v1.json"
IDENTITY_HASH = "sha256:7fe944b94b3796a55124388d9ef4228df5e0aca1daf45d5c10c7b87ca1b54490"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_011_rearrangement_reaction_pre_source_v1.json"
PRESEAL_HASH = "sha256:261ca2fed579e3a02906c04edf3c7e44fd5c752ecf6abfb3b24f08945e682b1c"
PRESEAL_PAYLOAD_HASH = "sha256:e624d9e2305b7ab53494816cd0bb8ca99a941ab3a4f63d675319bbc6019f7af7"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-011-europe-pmc-blind-v1"
ARCHIVE_NAME = "PMC8247891_SupplementaryFiles.zip"
URI = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8247891/supplementaryFiles"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    if digest_file(IDENTITY) != IDENTITY_HASH or digest_file(PRESEAL) != PRESEAL_HASH:
        raise SystemExit("ORG-011 identity or prediction seal changed")
    seal = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash")
    if claimed != PRESEAL_PAYLOAD_HASH or sha256_identity(seal) != PRESEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-011 canonical prediction seal changed")
    if OUTPUT.exists():
        raise SystemExit("ORG-011 source already captured; recapture prohibited")

    request = urllib.request.Request(URI, headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
        headers = dict(response.headers.items())
        status = response.status
    if status != 200 or not payload.startswith(b"PK"):
        raise SystemExit("ORG-011 supplementary archive capture failed")

    archive = zipfile.ZipFile(io.BytesIO(payload))
    members = tuple(info for info in archive.infolist() if not info.is_dir())
    if not members or not any(info.filename.casefold().endswith(".pdf") for info in members):
        raise SystemExit("ORG-011 supplementary archive contains no PDF")
    OUTPUT.mkdir(parents=True)
    archive_path = OUTPUT / ARCHIVE_NAME
    archive_path.write_bytes(payload)
    member_rows = []
    for info in members:
        name = Path(info.filename).name
        if name != info.filename or not name:
            raise SystemExit("ORG-011 archive contains an unsafe member path")
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
        "schema": "sft-v3-chemistry-org-011-source-inventory/1",
        "claim_id": "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011",
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
