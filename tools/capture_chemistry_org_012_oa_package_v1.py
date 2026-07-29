#!/usr/bin/env python3
"""Capture the preregistered ORG-012 open-access package exactly once."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_012_target_identities_v1.json"
IDENTITY_HASH = "sha256:28bb4368b39d7249ad5a561bb97e9f96674036fcc433194f4b07d1bdba1d1afa"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_012_pericyclic_reaction_pre_source_v1.json"
PRESEAL_FILE_HASH = "sha256:fdde5db01fad8cedbfea089099924d710d9a1a8d7e6d9954867d0e4f169aff6b"
PRESEAL_PAYLOAD_HASH = "sha256:8c0734c27d86bf7dad75a3fa4399742dbb09566c6d6e828faa59abeea636c8d2"
OA_RECORD_URI = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC8162770"
PACKAGE_URI = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/c9/18/PMC8162770.tar.gz"
MIGRATED_PACKAGE_URI = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/deprecated/oa_package/c9/18/PMC8162770.tar.gz"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def request_bytes(uri: str) -> tuple[bytes, dict[str, object]]:
    request = urllib.request.Request(
        uri,
        headers={"User-Agent": "Ernos-Labs-SFT-v3-evidence-capture/1"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = response.read()
        record = {
            "requested_uri": uri,
            "final_uri": response.geturl(),
            "http_status": response.status,
            "response_headers": dict(response.headers.items()),
        }
    if record["http_status"] != 200 or not payload:
        raise SystemExit(f"ORG-012 source capture failed: {uri}")
    return payload, record


def safe_member_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise SystemExit(f"ORG-012 unsafe archive member: {name}")
    return path


def main() -> None:
    if digest_file(IDENTITY) != IDENTITY_HASH or digest_file(PRESEAL) != PRESEAL_FILE_HASH:
        raise SystemExit("ORG-012 target identity or prediction seal changed")
    seal = json.loads(PRESEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash")
    if claimed != PRESEAL_PAYLOAD_HASH or sha256_identity(seal) != PRESEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-012 canonical prediction seal changed")
    if OUTPUT.exists():
        raise SystemExit("ORG-012 official source already captured; recapture prohibited")

    oa_payload, oa_transport = request_bytes(OA_RECORD_URI)
    registered_transport: dict[str, object]
    try:
        package_payload, package_transport = request_bytes(PACKAGE_URI)
        registered_transport = {
            "requested_uri": PACKAGE_URI,
            "result": "registered_transport_available",
        }
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        registered_transport = {
            "requested_uri": PACKAGE_URI,
            "http_status": error.code,
            "result": "registered_legacy_transport_moved_by_ncbi_2026_distribution_change",
        }
        package_payload, package_transport = request_bytes(MIGRATED_PACKAGE_URI)
    if not package_payload.startswith(b"\x1f\x8b"):
        raise SystemExit("ORG-012 official package is not the registered gzip archive")

    rows: list[dict[str, object]] = []
    extracted: list[tuple[PurePosixPath, bytes]] = []
    seen: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(package_payload), mode="r:gz") as archive:
        for ordinal, member in enumerate(archive.getmembers(), 1):
            member_path = safe_member_name(member.name)
            if member.name in seen:
                raise SystemExit(f"ORG-012 duplicate archive member: {member.name}")
            seen.add(member.name)
            row: dict[str, object] = {
                "ordinal": ordinal,
                "name": member.name,
                "member_type": "file" if member.isfile() else "directory" if member.isdir() else "other",
                "declared_size": member.size,
            }
            if member.isfile():
                handle = archive.extractfile(member)
                if handle is None:
                    raise SystemExit(f"ORG-012 unreadable archive member: {member.name}")
                content = handle.read()
                if len(content) != member.size:
                    raise SystemExit(f"ORG-012 archive-member size changed: {member.name}")
                row["content_sha256"] = digest_bytes(content)
                extracted.append((member_path, content))
            rows.append(row)

    OUTPUT.mkdir(parents=True)
    archive_path = OUTPUT / "PMC8162770.tar.gz"
    archive_path.write_bytes(package_payload)
    oa_path = OUTPUT / "oa-record.xml"
    oa_path.write_bytes(oa_payload)
    members_root = OUTPUT / "members"
    for member_path, content in extracted:
        target = members_root.joinpath(*member_path.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    inventory = {
        "schema": "sft-v3-chemistry-org-012-oa-source-inventory/1",
        "claim_id": "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012",
        "capture_status": "captured_once_after_claim_specific_value_free_seal",
        "source_recapture_count": 0,
        "oa_record_transport": oa_transport,
        "oa_record_path": oa_path.relative_to(ROOT).as_posix(),
        "oa_record_bytes": len(oa_payload),
        "oa_record_sha256": digest_bytes(oa_payload),
        "package_transport": package_transport,
        "registered_legacy_package_transport": registered_transport,
        "transport_resolution": "same registered PMC8162770 archive identity at NCBI's migrated deprecated prefix",
        "package_path": archive_path.relative_to(ROOT).as_posix(),
        "package_bytes": len(package_payload),
        "package_sha256": digest_bytes(package_payload),
        "archive_member_count": len(rows),
        "archive_regular_file_count": len(extracted),
        "archive_members_in_source_order": rows,
        "target_identity_path": IDENTITY.relative_to(ROOT).as_posix(),
        "target_identity_sha256": IDENTITY_HASH,
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_file_sha256": PRESEAL_FILE_HASH,
        "prediction_seal_payload_sha256": PRESEAL_PAYLOAD_HASH,
        "all_archive_members_preserved": True,
        "favorable_adverse_absent_and_unresolved_rows_filtered_during_capture": False,
    }
    inventory_path = OUTPUT / "source-inventory-v1.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "package_sha256": inventory["package_sha256"],
        "package_bytes": inventory["package_bytes"],
        "archive_member_count": inventory["archive_member_count"],
        "archive_regular_file_count": inventory["archive_regular_file_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
