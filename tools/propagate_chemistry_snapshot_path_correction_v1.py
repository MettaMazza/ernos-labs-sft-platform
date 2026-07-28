#!/usr/bin/env python3
"""Propagate only the authorized Chemistry snapshot path/hash correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_MANIFEST = ROOT / "audits/archives/chemistry_pre_readmission_2026-07-27/authority_manifest.json"
MIGRATION_MANIFEST = ROOT / "audits/CHEMISTRY_SNAPSHOT_PATH_CORRECTION_2026-07-27.json"
OLD_TO_NEW_PATH = {
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
PRE_READMISSION_HASH_OVERRIDES = {
    "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json":
        "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1",
    "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json":
        "sha256:00ed97e8dec313d65d2b9f6af595e3e3787a99aa60b86814f1a00f318abf011e",
}


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def candidates() -> tuple[Path, ...]:
    roots = (
        ROOT / "sft/chemistry",
        ROOT / "experiments/external_sources/chemistry",
        ROOT / "experiments/chemistry",
    )
    files: set[Path] = set()
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".py", ".md"}:
                files.add(path)
    for path in (ROOT / "tools").glob("*chemistry*"):
        if path.is_file() and path.suffix in {".py", ".json", ".md"}:
            files.add(path)
    for name in (
        "CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json",
        "CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json",
    ):
        files.add(ROOT / "audits" / name)
    # Migration/archive records describe the pre-correction identities and must
    # remain stable evidence, not become inputs to their own hash propagation.
    files.discard(ROOT / "tools/archive_chemistry_pre_readmission_v1.py")
    files.discard(ROOT / "tools/propagate_chemistry_snapshot_path_correction_v1.py")
    return tuple(sorted(files))


def main() -> None:
    archived = json.loads(ARCHIVE_MANIFEST.read_text(encoding="utf-8"))
    old_hash_by_path = {
        row["path"]: row["sha256"]
        for row in (*archived["archived_files"], *archived["external_source_hash_ledger"])
    }
    paths = candidates()
    baseline = {
        path: PRE_READMISSION_HASH_OVERRIDES.get(
            path.relative_to(ROOT).as_posix(),
            old_hash_by_path.get(path.relative_to(ROOT).as_posix()),
        )
        for path in paths
    }
    before = {path: digest(path) for path in paths}
    known_hashes = {
        path: {value for value in (baseline[path], before[path]) if value is not None}
        for path in paths
    }
    total_replacements = 0
    passes = 0
    while True:
        passes += 1
        current = {path: digest(path) for path in paths}
        replacements: dict[str, str] = {}
        for path in paths:
            for known in known_hashes[path]:
                if known != current[path]:
                    replacements[known] = current[path]
            known_hashes[path].add(current[path])
        replacements = {old: new for old, new in replacements.items() if old != new}
        changed = 0
        for path in paths:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            updated = text
            for old, new in OLD_TO_NEW_PATH.items():
                updated = updated.replace(old, new)
            for old, new in replacements.items():
                updated = updated.replace(old, new)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
        total_replacements += changed
        if changed == 0:
            break
        if passes >= 20:
            raise RuntimeError("Chemistry provenance-hash propagation did not reach a finite fixed point")

    after = {path: digest(path) for path in paths}
    changed_rows = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        old = baseline[path] or before[path]
        if old != after[path]:
            changed_rows.append({
                "path": relative,
                "pre_readmission_sha256": old,
                "corrected_sha256": after[path],
            })

    snapshot_rows = []
    archived_corrections = {row["old_path"]: row for row in archived["snapshot_type_corrections"]}
    for old, new in OLD_TO_NEW_PATH.items():
        row = archived_corrections[old]
        new_path = ROOT / new
        if digest(new_path) != row["sha256"]:
            raise RuntimeError(f"snapshot bytes changed during path correction: {new}")
        snapshot_rows.append({
            "old_path": old,
            "corrected_path": new,
            "content_type": "text/html",
            "bytes": new_path.stat().st_size,
            "sha256_before_and_after": row["sha256"],
        })

    migration = {
        "schema": "sft-v3-chemistry-snapshot-path-correction/1",
        "migration_date": "2026-07-27",
        "authorization": "Maria Smith explicitly authorized the complete Chemistry correction and clean re-admission.",
        "scientific_outcome_or_candidate_rule_changed": False,
        "engine_changed": False,
        "protected_validator_or_gate_changed": False,
        "existing_receipt_changed_or_deleted": False,
        "pre_readmission_archive_manifest": ARCHIVE_MANIFEST.relative_to(ROOT).as_posix(),
        "pre_readmission_archive_sha256": digest(ARCHIVE_MANIFEST),
        "snapshot_corrections": snapshot_rows,
        "provenance_propagation_passes": passes,
        "files_with_provenance_updates": changed_rows,
        "file_count_with_provenance_updates": len(changed_rows),
        "scope_statement": "Only filename content-type corrections and their mechanically forced path/hash descendants are changed. Every captured source byte, observed value, candidate grammar, survivor rule, adverse row and old receipt remains preserved.",
    }
    MIGRATION_MANIFEST.write_text(json.dumps(migration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Chemistry snapshot-path propagation: PASS snapshots={len(snapshot_rows)} "
        f"updated_files={len(changed_rows)} passes={passes}"
    )


if __name__ == "__main__":
    main()
