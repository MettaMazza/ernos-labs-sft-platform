#!/usr/bin/env python3
"""Capture the preregistered ORG-013 official OA package exactly once."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import urllib.error
import urllib.request
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.engine.canonical import sha256_identity  # noqa: E402

IDENTITY = ROOT / "experiments/external_sources/chemistry/org_013_target_identities_v1.json"
IDENTITY_HASH = "sha256:8f8793cad5c1cbf5cc51594197c8f43d75dc2a7e54fc1ac2006389a240fe4044"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_013_radical_network_pre_source_v1.json"
PRESEAL_PAYLOAD_HASH = "sha256:7b0568465f6f9762dea5fb4638d89635a6411dd2eafb2b17d4a9dd5af38d2d4a"
OA_RECORD_URI = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC11598545"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def request_bytes(uri: str) -> tuple[bytes, dict[str, object]]:
    request = urllib.request.Request(uri, headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = response.read()
        transport = {
            "requested_uri": uri,
            "final_uri": response.geturl(),
            "http_status": response.status,
            "response_headers": dict(response.headers.items()),
        }
    if transport["http_status"] != 200 or not payload:
        raise SystemExit(f"ORG-013 source capture failed: {uri}")
    return payload, transport


def safe_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise SystemExit(f"ORG-013 unsafe archive member: {name}")
    return path


def main() -> None:
    if digest_file(IDENTITY) != IDENTITY_HASH or OUTPUT.exists():
        raise SystemExit("ORG-013 identity changed or source already captured")
    seal = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash")
    if claimed != PRESEAL_PAYLOAD_HASH or sha256_identity(seal) != PRESEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-013 canonical prediction seal changed")

    oa_payload, oa_transport = request_bytes(OA_RECORD_URI)
    record = ET.fromstring(oa_payload)
    link = record.find(".//link[@format='tgz']")
    if link is None or "PMC11598545.tar.gz" not in link.get("href", ""):
        raise SystemExit("ORG-013 official OA package identity changed")
    registered_uri = link.get("href")
    https_uri = registered_uri.replace("ftp://", "https://", 1)
    legacy_transport: dict[str, object]
    try:
        package_payload, package_transport = request_bytes(https_uri)
        legacy_transport = {"requested_uri": https_uri, "result": "registered_transport_available"}
    except urllib.error.HTTPError as error:
        if error.code != 404 or "/pub/pmc/oa_package/" not in https_uri:
            raise
        legacy_transport = {"requested_uri": https_uri, "http_status": error.code, "result": "legacy_transport_moved"}
        migrated_uri = https_uri.replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/", 1)
        package_payload, package_transport = request_bytes(migrated_uri)
    if not package_payload.startswith(b"\x1f\x8b"):
        raise SystemExit("ORG-013 official package is not gzip")

    rows = []
    extracted = []
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(package_payload), mode="r:gz") as archive:
        for ordinal, member in enumerate(archive.getmembers(), 1):
            path = safe_name(member.name)
            if member.name in seen:
                raise SystemExit(f"ORG-013 duplicate member: {member.name}")
            seen.add(member.name)
            row = {"ordinal": ordinal, "name": member.name, "declared_size": member.size,
                   "member_type": "file" if member.isfile() else "directory" if member.isdir() else "other"}
            if member.isfile():
                handle = archive.extractfile(member)
                content = handle.read() if handle is not None else b""
                if len(content) != member.size:
                    raise SystemExit(f"ORG-013 member size changed: {member.name}")
                row["content_sha256"] = digest_bytes(content)
                extracted.append((path, content))
            rows.append(row)

    OUTPUT.mkdir(parents=True)
    archive_path = OUTPUT / "PMC11598545.tar.gz"
    archive_path.write_bytes(package_payload)
    oa_path = OUTPUT / "oa-record.xml"
    oa_path.write_bytes(oa_payload)
    for path, content in extracted:
        target = OUTPUT / "members" / Path(*path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    inventory = {
        "schema": "sft-v3-chemistry-org-013-oa-source-inventory/1",
        "claim_id": "SFT-CHEM-RADICAL-REACTION-NETWORK-013",
        "capture_status": "captured_once_after_claim_specific_value_free_seal",
        "source_recapture_count": 0,
        "oa_record_transport": oa_transport,
        "oa_record_path": oa_path.relative_to(ROOT).as_posix(),
        "oa_record_sha256": digest_bytes(oa_payload),
        "registered_oa_package_uri": registered_uri,
        "registered_legacy_transport": legacy_transport,
        "package_transport": package_transport,
        "package_path": archive_path.relative_to(ROOT).as_posix(),
        "package_bytes": len(package_payload),
        "package_sha256": digest_bytes(package_payload),
        "archive_member_count": len(rows),
        "archive_regular_file_count": len(extracted),
        "archive_members_in_source_order": rows,
        "target_identity_path": IDENTITY.relative_to(ROOT).as_posix(),
        "target_identity_sha256": IDENTITY_HASH,
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_payload_sha256": PRESEAL_PAYLOAD_HASH,
        "all_archive_members_preserved": True,
        "favorable_adverse_absent_and_unresolved_rows_filtered_during_capture": False,
    }
    (OUTPUT / "source-inventory-v1.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: inventory[k] for k in ("package_sha256", "package_bytes", "archive_member_count", "archive_regular_file_count")}, sort_keys=True))


if __name__ == "__main__":
    main()
