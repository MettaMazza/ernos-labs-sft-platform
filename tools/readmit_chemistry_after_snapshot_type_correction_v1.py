#!/usr/bin/env python3
"""One-time, archive-backed Chemistry clean re-admission through the frozen engine."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ARCHIVE = ROOT / "audits/archives/chemistry_pre_readmission_2026-07-27/authority_manifest.json"
CORRECTION = ROOT / "audits/CHEMISTRY_SNAPSHOT_PATH_CORRECTION_2026-07-27.json"
AUDIT = ROOT / "audits/CHEMISTRY_CLEAN_READMISSION_2026-07-27.json"
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
PATH_CORRECTIONS = {
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-g02620.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-g02620.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-ht06789.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-ht06789.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-o04308.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-o04308.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-s05735.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-s05735.html",
    "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05194.json":
        "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05194.html",
}


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", suffix=".pending", delete=False
    ) as handle:
        handle.write(rendered)
        pending = Path(handle.name)
    pending.replace(path)


def load_execution(entry: dict[str, object]):
    relative = entry["execution_file"]
    path = ROOT / str(relative)
    definition = importlib.util.spec_from_file_location(
        "sft_chemistry_readmission_" + str(entry["claim_id"]).replace("-", "_"), path
    )
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load Chemistry execution: {relative}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def scientific_view(value: object) -> object:
    """Remove identity-only fields while retaining every scientific statement and result."""

    if isinstance(value, dict):
        return {
            key: scientific_view(item)
            for key, item in value.items()
            if "hash" not in key.lower() and key not in {"engine_receipt_path"}
        }
    if isinstance(value, (list, tuple)):
        return [scientific_view(item) for item in value]
    if isinstance(value, str):
        corrected = value
        for old, new in PATH_CORRECTIONS.items():
            corrected = corrected.replace(old, new)
        return corrected
    return value


def write_if_changed(path: Path, payload: object) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.read_text(encoding="utf-8") != rendered:
        path.write_text(rendered, encoding="utf-8")


def materialize_package(claim_id: str, execution, receipt, census_row: dict[str, object], captured) -> bool:
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured.get("empirical")
    package = ROOT / "claims" / claim_id
    decision_name = "elimination_receipt.json"
    if not (package / decision_name).is_file():
        decision_name = "rearrangement_receipt.json"
    generated = {
        "candidate_census.json": {"claim_id": claim_id, **asdict(sealed.census)},
        decision_name: {
            "claim_id": claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": claim_id, "controls": asdict(sealed)["controls"]},
    }
    if empirical is not None:
        generated["empirical_validation.json"] = {"claim_id": claim_id, **asdict(empirical)}

    invariants = []
    for name, payload in generated.items():
        old = json.loads((package / name).read_text(encoding="utf-8"))
        invariants.append(scientific_view(old) == scientific_view(payload))
    if not all(invariants):
        raise RuntimeError(f"scientific payload changed during provenance-only re-admission: {claim_id}")

    for name, payload in generated.items():
        write_if_changed(package / name, payload)

    certificate_path = package / "certificate.json"
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    replacements: dict[str, str] = {}

    def replace(field: str, value: object) -> None:
        old = certificate.get(field)
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

    archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    if archive["engine_seal"] != ENGINE_SEAL or archive["verification_authority_seal"] != AUTHORITY_SEAL:
        raise SystemExit("archived engine or verification authority identity differs from the canonical seals")
    if correction.get("engine_changed") or correction.get("protected_validator_or_gate_changed"):
        raise SystemExit("snapshot correction records an unauthorized authority change")
    archive_zip = ROOT / archive["archive_zip_path"]
    if sha256(archive_zip) != archive["archive_zip_sha256"]:
        raise SystemExit("pre-readmission Chemistry authority archive has changed")

    census_path = ROOT / "census/claims.json"
    manifest_path = ROOT / "census/execution_manifest.json"
    original_census = json.loads(census_path.read_text(encoding="utf-8"))
    original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    original_ids = [row["claim_id"] for row in original_census["claims"]]
    if original_ids != [row["claim_id"] for row in original_manifest["claims"]]:
        raise SystemExit("census and execution manifest are not aligned before Chemistry re-admission")
    chemistry_ids = archive["chemistry_claim_ids_in_original_order"]
    chemistry_set = set(chemistry_ids)
    current_chemistry_rows = [row for row in original_census["claims"] if row["claim_id"] in chemistry_set]
    current_chemistry_manifest = [row for row in original_manifest["claims"] if row["claim_id"] in chemistry_set]
    if current_chemistry_rows != archive["chemistry_census_rows"]:
        raise SystemExit("live Chemistry census is not the archived pre-readmission authority surface")
    if current_chemistry_manifest != archive["chemistry_execution_rows"]:
        raise SystemExit("live Chemistry execution order is not the archived pre-readmission order")

    position = {claim_id: index for index, claim_id in enumerate(original_ids)}
    for entry in current_chemistry_manifest:
        execution = load_execution(entry)
        for dependency in execution.program.registration.dependencies:
            if dependency not in position or position[dependency] >= position[entry["claim_id"]]:
                raise SystemExit(f"Chemistry dependency is not earlier in the registered order: {entry['claim_id']}")

    retired_census = dict(original_census)
    retired_census["claims"] = [row for row in original_census["claims"] if row["claim_id"] not in chemistry_set]
    retired_manifest = dict(original_manifest)
    retired_manifest["claims"] = [row for row in original_manifest["claims"] if row["claim_id"] not in chemistry_set]
    atomic_json(census_path, retired_census)
    atomic_json(manifest_path, retired_manifest)

    old_by_id = {row["claim_id"]: row for row in archive["chemistry_census_rows"]}
    results = []
    try:
        repository = EngineRepository(ROOT)
        for index, entry in enumerate(current_chemistry_manifest, 1):
            claim_id = str(entry["claim_id"])
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

            empirical = CaptureEmpirical() if execution.empirical_validator is not None else None
            receipt = repository.execute_official(
                execution.program,
                CaptureIndependent(),
                execution.source_files,
                empirical,
            )
            if not receipt.model_admitted:
                raise RuntimeError(f"Chemistry claim did not re-enter the model: {claim_id}")
            live_census = json.loads(census_path.read_text(encoding="utf-8"))
            census_row = next(row for row in live_census["claims"] if row["claim_id"] == claim_id)
            live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            live_manifest["claims"].append(entry)
            atomic_json(manifest_path, live_manifest)
            invariant = materialize_package(claim_id, execution, receipt, census_row, captured)
            old_row = old_by_id[claim_id]
            results.append({
                "position": index,
                "claim_id": claim_id,
                "old_receipt_hash": old_row["receipt_hash"],
                "old_receipt_path": old_row["receipt_path"],
                "new_receipt_hash": receipt.receipt_hash,
                "new_receipt_path": census_row["receipt_path"],
                "receipt_identity_changed": old_row["receipt_hash"] != receipt.receipt_hash,
                "model_admitted": receipt.model_admitted,
                "scientific_payload_invariant": invariant,
            })
            if index == 1 or index % 10 == 0 or index == len(current_chemistry_manifest):
                print(
                    f"Chemistry clean re-admission: {index}/{len(current_chemistry_manifest)} pass; "
                    f"changed identities={sum(row['receipt_identity_changed'] for row in results)}",
                    flush=True,
                )

        live_census = json.loads(census_path.read_text(encoding="utf-8"))
        live_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows_by_id = {row["claim_id"]: row for row in live_census["claims"]}
        entries_by_id = {row["claim_id"]: row for row in live_manifest["claims"]}
        if set(rows_by_id) != set(original_ids) or set(entries_by_id) != set(original_ids):
            raise RuntimeError("re-admitted Chemistry surface does not restore the full census identity set")
        live_census["claims"] = [rows_by_id[claim_id] for claim_id in original_ids]
        live_manifest["claims"] = [entries_by_id[claim_id] for claim_id in original_ids]
        atomic_json(census_path, live_census)
        atomic_json(manifest_path, live_manifest)
    except BaseException:
        atomic_json(census_path, original_census)
        atomic_json(manifest_path, original_manifest)
        raise

    old_receipts_preserved = all((ROOT / row["old_receipt_path"]).is_file() for row in results)
    audit = {
        "schema": "sft-v3-chemistry-clean-readmission/1",
        "date": "2026-07-27",
        "authorization": archive["authorization"],
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "engine_or_protected_validator_changed": False,
        "old_receipt_changed_or_deleted": False,
        "pre_readmission_archive_manifest": ARCHIVE.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_manifest_sha256": sha256(ARCHIVE),
        "pre_readmission_archive_zip": archive["archive_zip_path"],
        "pre_readmission_archive_zip_sha256": archive["archive_zip_sha256"],
        "snapshot_correction_manifest": CORRECTION.relative_to(ROOT).as_posix(),
        "snapshot_correction_manifest_sha256": sha256(CORRECTION),
        "claim_count": len(results),
        "all_claims_model_admitted": all(row["model_admitted"] for row in results),
        "all_scientific_payloads_invariant": all(row["scientific_payload_invariant"] for row in results),
        "old_receipts_preserved": old_receipts_preserved,
        "dependency_order_violation_count": 0,
        "changed_receipt_identity_count": sum(row["receipt_identity_changed"] for row in results),
        "unchanged_receipt_identity_count": sum(not row["receipt_identity_changed"] for row in results),
        "claims": results,
    }
    atomic_json(AUDIT, audit)
    print(
        "CHEMISTRY CLEAN READMISSION: PASS "
        f"claims={len(results)} changed={audit['changed_receipt_identity_count']} "
        f"unchanged={audit['unchanged_receipt_identity_count']} old_receipts_preserved={old_receipts_preserved}",
        flush=True,
    )


if __name__ == "__main__":
    main()
