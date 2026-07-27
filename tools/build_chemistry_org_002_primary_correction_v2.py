#!/usr/bin/env python3
"""Correct only the preserved ORG-002 signed-charge search-scope defect."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_002_target_identities_v1.json"
IDENTITY_HASH = "sha256:d90bb68121cb37ea8a2d85242fd0b3ba4673ec9e3eb01d151c79fb8118b0fbbc"
V1_TARGET = ROOT / "experiments/external_sources/chemistry/org_002_withheld_targets_v1.json"
V1_TARGET_HASH = "sha256:18df21662ac89606b6d6e3cd2c7c80247b20cfe86156a97f85f1375f74185dbd"
V1_PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-002-primary-records-v1.json"
V1_PRIMARY_HASH = "sha256:f573789510a6349d997dc58ab4d2a2dbd6cbc361da7874f44c673e094540d8b5"
V2_TARGET = ROOT / "experiments/external_sources/chemistry/org_002_withheld_targets_v2.json"
V2_PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-002-primary-records-v2.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if V2_TARGET.exists() or V2_PRIMARY.exists():
        raise SystemExit("ORG-002 V2 correction already exists; preserved without replay")
    for path, expected in (
        (IDENTITY, IDENTITY_HASH),
        (V1_TARGET, V1_TARGET_HASH),
        (V1_PRIMARY, V1_PRIMARY_HASH),
    ):
        if hash_file(path) != expected:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-002 correction predecessor changed: {path}")

    target = json.loads(V1_TARGET.read_text(encoding="utf-8"))
    primary = json.loads(V1_PRIMARY.read_text(encoding="utf-8"))
    rows = target.get("rows", [])
    if len(rows) != 4:
        raise SystemExit("VOID_INVALID_HALTED: ORG-002 target census changed")
    searchable = "\n".join(
        json.dumps(row["source_outcome"]["complete_term_record"], sort_keys=True, ensure_ascii=False)
        for row in rows
    )
    if "^{-}" not in searchable or "O^{-}" not in searchable:
        raise SystemExit("VOID_INVALID_HALTED: registered external charge inscription absent")

    target["schema"] = "sft-v3-postseal-complete-target-vector-correction/2"
    target["preserved_predecessor"] = (str(V1_TARGET.relative_to(ROOT)), V1_TARGET_HASH)
    target["correction_scope"] = (
        "The V1 analysis searched only two of four complete preserved term records for a signed "
        "charge inscription. V2 searches the already captured four-record vector; no source, "
        "identity, target outcome, law, prediction, role or payload hash changed."
    )
    write_json(V2_TARGET, target)

    analysis = primary["exact_postseal_analysis"]
    if analysis.get("external_signed_charge_inscription_preserved") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-002 V1 adverse result changed")
    analysis["external_signed_charge_inscription_preserved"] = True
    analysis["preserved_v1_charge_search_scope_false_result_count"] = 1
    analysis["v2_corrected_complete_record_search_count"] = 4
    analysis["complete_target_vector_hash"] = sha256_identity(
        tuple((row["target_id"], row["source_outcome"]) for row in rows)
    )
    primary["schema"] = "sft-v3-postseal-primary-analysis-correction/2"
    primary["preserved_predecessors"] = {
        "target": (str(V1_TARGET.relative_to(ROOT)), V1_TARGET_HASH),
        "primary": (str(V1_PRIMARY.relative_to(ROOT)), V1_PRIMARY_HASH),
    }
    primary["target_registry"] = (str(V2_TARGET.relative_to(ROOT)), hash_file(V2_TARGET))
    write_json(V2_PRIMARY, primary)
    print(f"{V2_TARGET.relative_to(ROOT)} {hash_file(V2_TARGET)}")
    print(f"{V2_PRIMARY.relative_to(ROOT)} {hash_file(V2_PRIMARY)}")
    print(json.dumps(analysis, sort_keys=True))


if __name__ == "__main__":
    main()
