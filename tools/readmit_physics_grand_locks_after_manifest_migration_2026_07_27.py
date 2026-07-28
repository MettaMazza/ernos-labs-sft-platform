#!/usr/bin/env python3
"""Re-admit the two terminal Physics locks after their inputs were refreshed."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import zipfile

from readmit_stale_source_manifest_claims_2026_07_27 import (
    ROOT,
    atomic_json,
    load_execution,
    materialize_package,
    sha256,
)


CLAIM_IDS = (
    "SFT-PHYS-GRAND-LOCK-TERMINAL-075",
    "SFT-PHYS-VALIDATION-GRAND-LOCK-076",
)
ARCHIVE_DIR = (
    ROOT
    / "audits"
    / "archives"
    / "physics_grand_lock_post_manifest_readmission_2026-07-27"
)
ARCHIVE_ZIP = ARCHIVE_DIR / "pre_readmission_evidence.zip"
ARCHIVE_MANIFEST = ARCHIVE_DIR / "authority_manifest.json"
AUDIT = (
    ROOT
    / "audits"
    / "PHYSICS_GRAND_LOCK_POST_MANIFEST_CLEAN_READMISSION_2026-07-27.json"
)
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def create_archive(
    census: dict[str, object],
    manifest: dict[str, object],
) -> dict[str, object]:
    if ARCHIVE_DIR.exists():
        raise RuntimeError(f"archive already exists: {ARCHIVE_DIR}")
    ARCHIVE_DIR.mkdir(parents=True)
    claim_set = set(CLAIM_IDS)
    census_rows = [
        row for row in census["claims"] if row["claim_id"] in claim_set
    ]
    execution_rows = [
        row for row in manifest["claims"] if row["claim_id"] in claim_set
    ]
    if [row["claim_id"] for row in census_rows] != list(CLAIM_IDS):
        raise RuntimeError("terminal Physics lock census order differs")
    if [row["claim_id"] for row in execution_rows] != list(CLAIM_IDS):
        raise RuntimeError("terminal Physics lock execution order differs")
    paths = {
        ROOT / "census" / "claims.json",
        ROOT / "census" / "execution_manifest.json",
    }
    stale_rows = []
    for row, entry in zip(census_rows, execution_rows):
        claim_id = str(row["claim_id"])
        execution = load_execution(entry)
        certificate_path = ROOT / "claims" / claim_id / "certificate.json"
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        old_source = certificate["source_manifest_hash"]
        current_source = execution.program.registration.source_hash
        if old_source == current_source:
            raise RuntimeError(f"terminal lock is not stale: {claim_id}")
        stale_rows.append(
            {
                "claim_id": claim_id,
                "old_source_manifest_hash": old_source,
                "current_source_manifest_hash": current_source,
            }
        )
        paths.add(ROOT / str(row["receipt_path"]))
        paths.update(
            path
            for path in (ROOT / "claims" / claim_id).rglob("*")
            if path.is_file()
        )
    with zipfile.ZipFile(ARCHIVE_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT).as_posix())
    payload = {
        "schema": "sft-v3-physics-grand-lock-post-manifest-pre-readmission/1",
        "date": "2026-07-27",
        "authorization": "Maria Smith: update the hash and complete the work",
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "claim_ids_in_original_order": list(CLAIM_IDS),
        "stale_source_manifest_rows": stale_rows,
        "census_rows": census_rows,
        "execution_rows": execution_rows,
        "archive_zip_path": ARCHIVE_ZIP.relative_to(ROOT).as_posix(),
        "archive_zip_sha256": sha256(ARCHIVE_ZIP),
        "archived_file_count": len(paths),
    }
    atomic_json(ARCHIVE_MANIFEST, payload)
    return payload


def restore(new_receipts: list[Path]) -> None:
    for path in new_receipts:
        if path.is_file():
            path.unlink()
    with zipfile.ZipFile(ARCHIVE_ZIP, "r") as archive:
        archive.extractall(ROOT)


def main() -> None:
    from sft.engine import EngineRepository

    census_path = ROOT / "census" / "claims.json"
    manifest_path = ROOT / "census" / "execution_manifest.json"
    original_census = json.loads(census_path.read_text(encoding="utf-8"))
    original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    original_ids = [row["claim_id"] for row in original_census["claims"]]
    if original_ids != [row["claim_id"] for row in original_manifest["claims"]]:
        raise SystemExit("census and execution manifest are not aligned")
    archive = create_archive(original_census, original_manifest)
    if sha256(ARCHIVE_ZIP) != archive["archive_zip_sha256"]:
        raise SystemExit("terminal-lock archive identity failed after creation")

    claim_set = set(CLAIM_IDS)
    retired_census = dict(original_census)
    retired_census["claims"] = [
        row for row in original_census["claims"] if row["claim_id"] not in claim_set
    ]
    retired_manifest = dict(original_manifest)
    retired_manifest["claims"] = [
        row for row in original_manifest["claims"] if row["claim_id"] not in claim_set
    ]
    atomic_json(census_path, retired_census)
    atomic_json(manifest_path, retired_manifest)

    entries = {row["claim_id"]: row for row in archive["execution_rows"]}
    old_rows = {row["claim_id"]: row for row in archive["census_rows"]}
    results = []
    new_receipts: list[Path] = []
    try:
        repository = EngineRepository(ROOT)
        for claim_id in CLAIM_IDS:
            entry = entries[claim_id]
            execution = load_execution(entry)
            captured: dict[str, object] = {}

            class CaptureIndependent:
                def validate(self, sealed):
                    captured["sealed"] = sealed
                    captured["external"] = execution.independent_validator.validate(sealed)
                    return captured["external"]

            class CaptureEmpirical:
                def validate(self, sealed):
                    captured["empirical"] = execution.empirical_validator.validate(sealed)
                    return captured["empirical"]

            empirical = (
                CaptureEmpirical() if execution.empirical_validator is not None else None
            )
            receipt = repository.execute_official(
                execution.program,
                CaptureIndependent(),
                execution.source_files,
                empirical,
            )
            if not receipt.model_admitted:
                raise RuntimeError(f"terminal lock did not re-enter model: {claim_id}")
            live_census = json.loads(census_path.read_text(encoding="utf-8"))
            census_row = next(
                row for row in live_census["claims"] if row["claim_id"] == claim_id
            )
            new_receipts.append(ROOT / str(census_row["receipt_path"]))
            live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            live_manifest["claims"].append(entry)
            atomic_json(manifest_path, live_manifest)
            invariant = materialize_package(
                claim_id, execution, receipt, census_row, captured
            )
            old = old_rows[claim_id]
            results.append(
                {
                    "claim_id": claim_id,
                    "old_receipt_hash": old["receipt_hash"],
                    "old_receipt_path": old["receipt_path"],
                    "new_receipt_hash": receipt.receipt_hash,
                    "new_receipt_path": census_row["receipt_path"],
                    "receipt_identity_changed": old["receipt_hash"] != receipt.receipt_hash,
                    "model_admitted": receipt.model_admitted,
                    "scientific_payload_invariant": invariant,
                }
            )
            print(f"Terminal Physics lock re-admission: {claim_id} pass", flush=True)

        live_census = json.loads(census_path.read_text(encoding="utf-8"))
        live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        census_by_id = {row["claim_id"]: row for row in live_census["claims"]}
        manifest_by_id = {row["claim_id"]: row for row in live_manifest["claims"]}
        live_census["claims"] = [census_by_id[claim_id] for claim_id in original_ids]
        live_manifest["claims"] = [manifest_by_id[claim_id] for claim_id in original_ids]
        atomic_json(census_path, live_census)
        atomic_json(manifest_path, live_manifest)
    except BaseException:
        restore(new_receipts)
        raise

    audit = {
        "schema": "sft-v3-physics-grand-lock-post-manifest-clean-readmission/1",
        "date": "2026-07-27",
        "authorization": archive["authorization"],
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "engine_or_protected_validator_changed": False,
        "old_receipt_changed_or_deleted": False,
        "claim_count": len(results),
        "all_claims_model_admitted": all(row["model_admitted"] for row in results),
        "all_scientific_payloads_invariant": all(
            row["scientific_payload_invariant"] for row in results
        ),
        "old_receipts_preserved": all(
            (ROOT / str(row["old_receipt_path"])).is_file() for row in results
        ),
        "pre_readmission_archive_manifest": ARCHIVE_MANIFEST.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_manifest_sha256": sha256(ARCHIVE_MANIFEST),
        "pre_readmission_archive_zip": ARCHIVE_ZIP.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_zip_sha256": sha256(ARCHIVE_ZIP),
        "claims": results,
    }
    atomic_json(AUDIT, audit)
    print(
        "PHYSICS GRAND LOCK POST-MANIFEST READMISSION: PASS "
        f"claims={len(results)} old_receipts_preserved={audit['old_receipts_preserved']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
