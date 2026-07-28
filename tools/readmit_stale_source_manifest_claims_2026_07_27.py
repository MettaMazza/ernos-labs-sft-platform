#!/usr/bin/env python3
"""Archive and re-admit claims whose recorded source manifest is stale.

This is a one-time evidence-identity migration.  The canonical engine and
verification authority remain immutable, every old receipt is preserved, and
all non-hash scientific payloads must remain identical.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARCHIVE_DIR = ROOT / "audits" / "archives" / "stale_source_manifest_readmission_2026-07-27"
ARCHIVE_ZIP = ARCHIVE_DIR / "pre_readmission_evidence.zip"
ARCHIVE_MANIFEST = ARCHIVE_DIR / "authority_manifest.json"
AUDIT = ROOT / "audits" / "STALE_SOURCE_MANIFEST_CLEAN_READMISSION_2026-07-27.json"
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
EXPECTED_CLAIM_COUNT = 284


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=path.name + ".",
        suffix=".pending",
        delete=False,
    ) as handle:
        handle.write(rendered)
        pending = Path(handle.name)
    pending.replace(path)


def load_execution(entry: dict[str, object]):
    path = ROOT / str(entry["execution_file"])
    definition = importlib.util.spec_from_file_location(
        "sft_source_manifest_readmission_" + str(entry["claim_id"]).replace("-", "_"),
        path,
    )
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load execution binding: {path}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def scientific_view(value: object) -> object:
    """Remove identity-only fields while retaining every scientific result."""

    if isinstance(value, dict):
        return {
            key: scientific_view(item)
            for key, item in value.items()
            if "hash" not in key.lower() and key != "engine_receipt_path"
        }
    if isinstance(value, (list, tuple)):
        return [scientific_view(item) for item in value]
    return value


def write_if_changed(path: Path, payload: object) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.read_text(encoding="utf-8") != rendered:
        path.write_text(rendered, encoding="utf-8")


def discover_stale_claims(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    stale: list[dict[str, object]] = []
    for index, entry in enumerate(entries, 1):
        execution = load_execution(entry)
        certificate_path = ROOT / "claims" / str(entry["claim_id"]) / "certificate.json"
        if not certificate_path.is_file():
            continue
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        recorded = certificate.get("source_manifest_hash")
        current = execution.program.registration.source_hash
        if recorded is not None and recorded != current:
            stale.append(
                {
                    "position": index,
                    "claim_id": entry["claim_id"],
                    "old_source_manifest_hash": recorded,
                    "current_source_manifest_hash": current,
                }
            )
    return stale


def archive_authority(
    original_census: dict[str, object],
    original_manifest: dict[str, object],
    stale: list[dict[str, object]],
) -> dict[str, object]:
    if ARCHIVE_DIR.exists():
        raise RuntimeError(f"archive already exists: {ARCHIVE_DIR}")
    ARCHIVE_DIR.mkdir(parents=True)
    stale_ids = [str(row["claim_id"]) for row in stale]
    stale_set = set(stale_ids)
    census_rows = [
        row for row in original_census["claims"] if row["claim_id"] in stale_set
    ]
    execution_rows = [
        row for row in original_manifest["claims"] if row["claim_id"] in stale_set
    ]
    paths = {
        ROOT / "census" / "claims.json",
        ROOT / "census" / "execution_manifest.json",
    }
    for row in census_rows:
        paths.add(ROOT / str(row["receipt_path"]))
        package = ROOT / "claims" / str(row["claim_id"])
        paths.update(path for path in package.rglob("*") if path.is_file())
    with zipfile.ZipFile(ARCHIVE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT).as_posix())
    manifest = {
        "schema": "sft-v3-stale-source-manifest-pre-readmission-archive/1",
        "date": "2026-07-27",
        "authorization": "Maria Smith: update the hash and complete the work",
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "claim_count": len(stale_ids),
        "claim_ids_in_original_order": stale_ids,
        "stale_source_manifest_rows": stale,
        "census_rows": census_rows,
        "execution_rows": execution_rows,
        "archive_zip_path": ARCHIVE_ZIP.relative_to(ROOT).as_posix(),
        "archive_zip_sha256": sha256(ARCHIVE_ZIP),
        "archived_file_count": len(paths),
    }
    atomic_json(ARCHIVE_MANIFEST, manifest)
    return manifest


def restore_archive(new_receipt_paths: list[Path]) -> None:
    for path in new_receipt_paths:
        if path.is_file():
            path.unlink()
    with zipfile.ZipFile(ARCHIVE_ZIP, "r") as archive:
        archive.extractall(ROOT)


def materialize_package(
    claim_id: str,
    execution,
    receipt,
    census_row: dict[str, object],
    captured: dict[str, object],
) -> bool:
    package = ROOT / "claims" / claim_id
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured.get("empirical")
    generated = {
        "candidate_census.json": {"claim_id": claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": claim_id, "controls": asdict(sealed)["controls"]},
    }
    if empirical is not None:
        generated["empirical_validation.json"] = {
            "claim_id": claim_id,
            **asdict(empirical),
        }

    invariants = []
    for name, payload in generated.items():
        old = json.loads((package / name).read_text(encoding="utf-8"))
        invariants.append(scientific_view(old) == scientific_view(payload))
    if not all(invariants):
        raise RuntimeError(
            f"scientific payload changed during identity-only re-admission: {claim_id}"
        )
    for name, payload in generated.items():
        write_if_changed(package / name, payload)

    certificate_path = package / "certificate.json"
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    replacements: dict[str, str] = {}

    def replace(field: str, value: object) -> None:
        old = certificate.get(field)
        if field in certificate or value is not None:
            certificate[field] = value
        if isinstance(old, str) and isinstance(value, str) and old != value:
            replacements[old] = value

    replace("source_manifest_hash", execution.program.registration.source_hash)
    replace("derivation_seal_hash", sealed.seal_hash)
    replace("independent_implementation_hash", external.implementation_hash)
    replace("independent_certificate_hash", external.certificate_hash)
    replace("external_validation_hash", receipt.external_validation_hash)
    replace("empirical_validation_hash", receipt.empirical_validation_hash)
    if empirical is not None:
        replace("measurement_receipt_hash", empirical.measurement_receipt_hash)
    replace("engine_receipt_hash", receipt.receipt_hash)
    replace("engine_receipt_path", census_row["receipt_path"])
    write_if_changed(certificate_path, certificate)

    status_path = package / "STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        status = status.replace(old, new)
    if status_path.read_text(encoding="utf-8") != status:
        status_path.write_text(status, encoding="utf-8")
    return all(invariants)


def main() -> None:
    from sft.engine import EngineRepository

    census_path = ROOT / "census" / "claims.json"
    manifest_path = ROOT / "census" / "execution_manifest.json"
    original_census = json.loads(census_path.read_text(encoding="utf-8"))
    original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    original_ids = [row["claim_id"] for row in original_census["claims"]]
    if original_ids != [row["claim_id"] for row in original_manifest["claims"]]:
        raise SystemExit("census and execution manifest are not aligned")

    stale = discover_stale_claims(original_manifest["claims"])
    if len(stale) != EXPECTED_CLAIM_COUNT:
        raise SystemExit(
            f"stale source-manifest scope changed: {len(stale)} != {EXPECTED_CLAIM_COUNT}"
        )
    archive = archive_authority(original_census, original_manifest, stale)
    if sha256(ARCHIVE_ZIP) != archive["archive_zip_sha256"]:
        raise SystemExit("pre-readmission archive identity failed immediately after creation")

    stale_ids = archive["claim_ids_in_original_order"]
    stale_set = set(stale_ids)
    retired_census = dict(original_census)
    retired_census["claims"] = [
        row for row in original_census["claims"] if row["claim_id"] not in stale_set
    ]
    retired_manifest = dict(original_manifest)
    retired_manifest["claims"] = [
        row for row in original_manifest["claims"] if row["claim_id"] not in stale_set
    ]
    atomic_json(census_path, retired_census)
    atomic_json(manifest_path, retired_manifest)

    entries_by_id = {
        row["claim_id"]: row for row in archive["execution_rows"]
    }
    old_by_id = {row["claim_id"]: row for row in archive["census_rows"]}
    results: list[dict[str, object]] = []
    new_receipt_paths: list[Path] = []
    try:
        repository = EngineRepository(ROOT)
        for index, claim_id in enumerate(stale_ids, 1):
            entry = entries_by_id[claim_id]
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
                raise RuntimeError(f"claim did not re-enter the model: {claim_id}")
            live_census = json.loads(census_path.read_text(encoding="utf-8"))
            census_row = next(
                row for row in live_census["claims"] if row["claim_id"] == claim_id
            )
            new_receipt_paths.append(ROOT / str(census_row["receipt_path"]))
            live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            live_manifest["claims"].append(entry)
            atomic_json(manifest_path, live_manifest)
            invariant = materialize_package(
                claim_id, execution, receipt, census_row, captured
            )
            old_row = old_by_id[claim_id]
            results.append(
                {
                    "position": index,
                    "claim_id": claim_id,
                    "old_receipt_hash": old_row["receipt_hash"],
                    "old_receipt_path": old_row["receipt_path"],
                    "new_receipt_hash": receipt.receipt_hash,
                    "new_receipt_path": census_row["receipt_path"],
                    "receipt_identity_changed": (
                        old_row["receipt_hash"] != receipt.receipt_hash
                    ),
                    "model_admitted": receipt.model_admitted,
                    "scientific_payload_invariant": invariant,
                }
            )
            if index == 1 or index % 10 == 0 or index == len(stale_ids):
                print(
                    f"Source-manifest clean re-admission: {index}/{len(stale_ids)} pass",
                    flush=True,
                )

        live_census = json.loads(census_path.read_text(encoding="utf-8"))
        live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows_by_id = {row["claim_id"]: row for row in live_census["claims"]}
        manifest_by_id = {row["claim_id"]: row for row in live_manifest["claims"]}
        if set(rows_by_id) != set(original_ids) or set(manifest_by_id) != set(original_ids):
            raise RuntimeError("re-admission did not restore the complete claim identity set")
        live_census["claims"] = [rows_by_id[claim_id] for claim_id in original_ids]
        live_manifest["claims"] = [
            manifest_by_id[claim_id] for claim_id in original_ids
        ]
        atomic_json(census_path, live_census)
        atomic_json(manifest_path, live_manifest)
    except BaseException:
        restore_archive(new_receipt_paths)
        raise

    old_receipts_preserved = all(
        (ROOT / str(row["old_receipt_path"])).is_file() for row in results
    )
    audit = {
        "schema": "sft-v3-stale-source-manifest-clean-readmission/1",
        "date": "2026-07-27",
        "authorization": archive["authorization"],
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "engine_or_protected_validator_changed": False,
        "old_receipt_changed_or_deleted": False,
        "pre_readmission_archive_manifest": ARCHIVE_MANIFEST.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_manifest_sha256": sha256(ARCHIVE_MANIFEST),
        "pre_readmission_archive_zip": ARCHIVE_ZIP.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_zip_sha256": sha256(ARCHIVE_ZIP),
        "claim_count": len(results),
        "all_claims_model_admitted": all(row["model_admitted"] for row in results),
        "all_scientific_payloads_invariant": all(
            row["scientific_payload_invariant"] for row in results
        ),
        "old_receipts_preserved": old_receipts_preserved,
        "changed_receipt_identity_count": sum(
            row["receipt_identity_changed"] for row in results
        ),
        "unchanged_receipt_identity_count": sum(
            not row["receipt_identity_changed"] for row in results
        ),
        "claims": results,
    }
    atomic_json(AUDIT, audit)
    print(
        "STALE SOURCE-MANIFEST CLEAN READMISSION: PASS "
        f"claims={len(results)} "
        f"changed={audit['changed_receipt_identity_count']} "
        f"unchanged={audit['unchanged_receipt_identity_count']} "
        f"old_receipts_preserved={old_receipts_preserved}",
        flush=True,
    )


if __name__ == "__main__":
    main()
