#!/usr/bin/env python3
"""Preserve refreshed certificates while restoring immutable Grand Lock inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SOURCE_ARCHIVE = (
    ROOT
    / "audits"
    / "archives"
    / "stale_source_manifest_readmission_2026-07-27"
    / "pre_readmission_evidence.zip"
)
SOURCE_MANIFEST = SOURCE_ARCHIVE.parent / "authority_manifest.json"
AUDIT = (
    ROOT
    / "audits"
    / "PHYSICS_GRAND_LOCK_HISTORICAL_CERTIFICATE_PRESERVATION_2026-07-27.json"
)
GRAND_LOCK_IDS = (
    "SFT-PHYS-GRAND-LOCK-TERMINAL-075",
    "SFT-PHYS-VALIDATION-GRAND-LOCK-076",
)
VERSIONED_NAME = "certificate.source-manifest-readmission-2026-07-27.json"
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def atomic_bytes(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=path.parent,
        prefix=path.name + ".",
        suffix=".pending",
        delete=False,
    ) as handle:
        handle.write(data)
        pending = Path(handle.name)
    pending.replace(path)


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_bytes(
        path,
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location(
        "sft_grand_lock_certificate_preservation_" + claim_id.replace("-", "_"),
        path,
    )
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load Grand Lock execution: {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if manifest["engine_seal"] != ENGINE_SEAL:
        raise SystemExit("source archive engine seal differs")
    if manifest["verification_authority_seal"] != AUTHORITY_SEAL:
        raise SystemExit("source archive verification-authority seal differs")
    if sha256(SOURCE_ARCHIVE) != manifest["archive_zip_sha256"]:
        raise SystemExit("source archive identity differs")

    archived_claims = set(manifest["claim_ids_in_original_order"])
    referenced_certificates: set[str] = set()
    before_hashes = {}
    for claim_id in GRAND_LOCK_IDS:
        execution = load_execution(claim_id)
        certificate = json.loads(
            (ROOT / "claims" / claim_id / "certificate.json").read_text(encoding="utf-8")
        )
        before_hashes[claim_id] = {
            "recorded_source_manifest_hash": certificate["source_manifest_hash"],
            "current_source_manifest_hash": execution.program.registration.source_hash,
        }
        for path in execution.source_files:
            if path.name != "certificate.json":
                continue
            relative = path.relative_to(ROOT).as_posix()
            parts = Path(relative).parts
            if len(parts) == 3 and parts[0] == "claims" and parts[1] in archived_claims:
                referenced_certificates.add(relative)

    records = []
    with zipfile.ZipFile(SOURCE_ARCHIVE, "r") as archive:
        archived_names = set(archive.namelist())
        for relative in sorted(referenced_certificates):
            if relative not in archived_names:
                raise RuntimeError(f"historical certificate absent from archive: {relative}")
            canonical = ROOT / relative
            refreshed = canonical.read_bytes()
            historical = archive.read(relative)
            versioned = canonical.with_name(VERSIONED_NAME)
            atomic_bytes(versioned, refreshed)
            atomic_bytes(canonical, historical)
            records.append(
                {
                    "claim_id": Path(relative).parts[1],
                    "canonical_certificate_path": relative,
                    "historical_certificate_sha256": digest_bytes(historical),
                    "versioned_refreshed_certificate_path": versioned.relative_to(ROOT).as_posix(),
                    "versioned_refreshed_certificate_sha256": digest_bytes(refreshed),
                    "historical_certificate_restored_exactly": (
                        canonical.read_bytes() == historical
                    ),
                    "refreshed_certificate_preserved_exactly": (
                        versioned.read_bytes() == refreshed
                    ),
                }
            )

    after_hashes = {}
    for claim_id in GRAND_LOCK_IDS:
        execution = load_execution(claim_id)
        certificate = json.loads(
            (ROOT / "claims" / claim_id / "certificate.json").read_text(encoding="utf-8")
        )
        after_hashes[claim_id] = {
            "recorded_source_manifest_hash": certificate["source_manifest_hash"],
            "current_source_manifest_hash": execution.program.registration.source_hash,
            "source_manifest_matches_immutable_lock": (
                certificate["source_manifest_hash"]
                == execution.program.registration.source_hash
            ),
        }
    if not all(
        row["source_manifest_matches_immutable_lock"] for row in after_hashes.values()
    ):
        raise RuntimeError("historical certificate restoration did not restore both locks")

    audit = {
        "schema": "sft-v3-physics-grand-lock-historical-certificate-preservation/1",
        "date": "2026-07-27",
        "authorization": "Maria Smith: no validation or engine changes; update the hash and complete the work",
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "engine_or_validator_changed": False,
        "historical_receipt_changed_or_deleted": False,
        "source_archive_manifest": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
        "source_archive_manifest_sha256": sha256(SOURCE_MANIFEST),
        "source_archive_zip": SOURCE_ARCHIVE.relative_to(ROOT).as_posix(),
        "source_archive_zip_sha256": sha256(SOURCE_ARCHIVE),
        "preserved_certificate_count": len(records),
        "all_historical_certificates_restored": all(
            row["historical_certificate_restored_exactly"] for row in records
        ),
        "all_refreshed_certificates_preserved": all(
            row["refreshed_certificate_preserved_exactly"] for row in records
        ),
        "grand_lock_source_hashes_before": before_hashes,
        "grand_lock_source_hashes_after": after_hashes,
        "certificates": records,
    }
    atomic_json(AUDIT, audit)
    print(
        "PHYSICS GRAND LOCK HISTORICAL CERTIFICATE PRESERVATION: PASS "
        f"certificates={len(records)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
