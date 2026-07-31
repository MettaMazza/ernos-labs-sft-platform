#!/usr/bin/env python3
"""Generate or verify the complete publishable Protein Fold machine manifest."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]
OUTPUT = WORKSPACE / "paper/MACHINE_ARCHIVE_MANIFEST.json"
EXCLUDED_PREFIXES = (
    "comparator/runtime/",
    "comparator/model_parameters/",
    "comparator/databases/",
)
EXCLUDED_EXACT = {
    "paper/MACHINE_ARCHIVE_MANIFEST.json",
}


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def excluded(relative: str) -> bool:
    parts = Path(relative).parts
    name = Path(relative).name
    return (
        relative in EXCLUDED_EXACT
        or relative.startswith(EXCLUDED_PREFIXES)
        or (
            relative.startswith("publication/")
            and "_publication_receipt_" in name
            and name.endswith(".json")
        )
        or "__pycache__" in parts
        or relative.endswith(".pyc")
        or ".tmp-" in name
        or name == ".DS_Store"
    )


def current_files() -> list[dict[str, Any]]:
    records = []
    for path in sorted(WORKSPACE.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(WORKSPACE).as_posix()
        if excluded(relative):
            continue
        records.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    return records


def category_summary(files: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for record in files:
        category = record["path"].split("/", 1)[0]
        row = summary.setdefault(category, {"file_count": 0, "total_bytes": 0})
        row["file_count"] += 1
        row["total_bytes"] += record["bytes"]
    return dict(sorted(summary.items()))


def content_root(files: list[dict[str, Any]]) -> str:
    value = sha256()
    for record in files:
        value.update(record["path"].encode("utf-8"))
        value.update(b"\0")
        value.update(str(record["bytes"]).encode("ascii"))
        value.update(b"\0")
        value.update(record["sha256"].encode("ascii"))
        value.update(b"\n")
    return value.hexdigest()


def build() -> dict[str, Any]:
    files = current_files()
    return {
        "schema": "sft-v3-protein-fold-machine-archive-manifest/v1",
        "status": "frozen_preliminary_publication_snapshot__active_computations_and_primary_campaign_assets_pending",
        "date": "2026-07-31",
        "authority": {
            "scientific_author": "Maria Smith",
            "publication_authority": "Maria Smith",
            "remote_publication_authorized": True,
            "remote_publication_authorization_scope": "authorised Zenodo successor preliminary-results release version 0.9.4 only",
            "protected_engine_edited": False,
        },
        "scope": {
            "root": "applications/frontier/v3_computational_proofs/protein_folding",
            "includes": "every current regular non-symlink file except the manifest itself and the explicit exclusions below",
            "excluded_prefixes": list(EXCLUDED_PREFIXES),
            "excluded_exact": sorted(EXCLUDED_EXACT),
            "automatic_exclusions": ["__pycache__ directories", "*.pyc", ".DS_Store", "active .tmp-* computation streams", "post-publication transaction receipts"],
            "exclusion_reason": "local runtime, restricted model parameters, full databases, generated cache files, active incomplete computation streams, post-publication transaction receipts and manifest self-reference are not frozen preliminary-publication payloads",
        },
        "archive_state": {
            "file_count": len(files),
            "total_bytes": sum(record["bytes"] for record in files),
            "content_root_sha256": content_root(files),
            "category_summary": category_summary(files),
        },
        "restricted_asset_state": {
            "alphafold3_model_parameters_included": False,
            "alphafold3_full_databases_included": False,
            "local_virtual_environment_included": False,
            "registered_source_archive_included": True,
            "normalized_local_environment_test_logs_included": True,
        },
        "completion_boundary": {
            "current_representation_and_custody_records_included": True,
            "development_favourable_adverse_and_unavailable_records_included": True,
            "canonical_evaluator_records_included": True,
            "primary_100_target_campaign_rows_available": False,
            "matched_alphafold3_campaign_rows_available": False,
            "parity_decision_available": False,
            "active_incomplete_computation_streams_excluded": True,
            "publication_version": "0.9.4",
            "publication_version_doi": "10.5281/zenodo.21717581",
            "manifest_must_be_regenerated_after_any_file_change": True,
        },
        "files": files,
    }


def write() -> int:
    manifest = build()
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["archive_state"], sort_keys=True))
    return 0


def verify() -> int:
    recorded = json.loads(OUTPUT.read_bytes())
    current = build()
    keys = ("file_count", "total_bytes", "content_root_sha256", "category_summary")
    failures = [
        key for key in keys
        if recorded["archive_state"].get(key) != current["archive_state"].get(key)
    ]
    if recorded.get("files") != current.get("files"):
        failures.append("files")
    print(json.dumps({
        "status": "pass" if not failures else "fail",
        "failure_count": len(failures),
        "failures": failures,
        "archive_state": current["archive_state"],
    }, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    raise SystemExit(verify() if args.verify else write())
