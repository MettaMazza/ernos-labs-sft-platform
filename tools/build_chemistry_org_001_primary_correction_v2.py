#!/usr/bin/env python3
"""Correct only the preserved ORG-001 uppercase-table-boundary parsing defect."""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_001_target_identities_v1.json"
IDENTITY_HASH = "sha256:8d63eeae30f819ec961ac73e98add98258ad48faa670d0ea140ed9bd2271a893"
V1_TARGET = ROOT / "experiments/external_sources/chemistry/org_001_withheld_targets_v1.json"
V1_TARGET_HASH = "sha256:adade1c9a6bed06b83a745680a63f73f0685cbf422bb4a2f3f5f0bf9830e0e7f"
V1_PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-001-primary-records-v1.json"
V1_PRIMARY_HASH = "sha256:bef1acc4528270b903349dfb49d87dd12548bd81cca90ffab1f15865821f5d28"
V2_TARGET = ROOT / "experiments/external_sources/chemistry/org_001_withheld_targets_v2.json"
V2_PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-001-primary-records-v2.json"
CORRECTED_ROLE = "complete-separated-double-bond-control-coordinate-surface"


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def table_after_case_insensitive(raw: str, marker: str) -> list[list[str]]:
    marker_match = re.search(re.escape(marker), raw, flags=re.I)
    if not marker_match:
        raise ValueError(f"registered marker absent: {marker}")
    table_match = re.search(r"<table\b[^>]*>.*?</table>", raw[marker_match.start():], flags=re.I | re.S)
    if not table_match:
        raise ValueError(f"registered table incomplete: {marker}")
    rows = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table_match.group(0), flags=re.I | re.S):
        cells = [
            text_only(cell)
            for cell in re.findall(r"<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>", row, flags=re.I | re.S)
        ]
        if cells:
            rows.append(cells)
    return rows


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if V2_TARGET.exists() or V2_PRIMARY.exists():
        raise SystemExit("ORG-001 V2 correction already exists; preserved without replay")
    for path, expected in (
        (IDENTITY, IDENTITY_HASH),
        (V1_TARGET, V1_TARGET_HASH),
        (V1_PRIMARY, V1_PRIMARY_HASH),
    ):
        if hash_file(path) != expected:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-001 correction predecessor changed: {path}")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    target = json.loads(V1_TARGET.read_text(encoding="utf-8"))
    primary = json.loads(V1_PRIMARY.read_text(encoding="utf-8"))
    corrected = 0
    for row in target["rows"]:
        if row["source_record_role"] != CORRECTED_ROLE:
            continue
        path = ROOT / row["snapshot_path"]
        if hash_file(path) != row["snapshot_sha256"]:
            raise SystemExit("VOID_INVALID_HALTED: ORG-001 control source changed")
        raw = path.read_text(encoding="utf-8", errors="replace")
        outcome = {
            "complete_internal_coordinate_table": table_after_case_insensitive(
                raw, "<H2>Internal coordinates</H2>"
            ),
            "complete_bond_description_table": table_after_case_insensitive(
                raw, "<h2>Bond descriptions</h2>"
            ),
        }
        row["source_outcome"] = outcome
        row["target_payload_hash"] = sha256_identity(
            (row["target_id"], row["source_record_role"], outcome)
        )
        corrected += 1
    if corrected != 1:
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 correction scope changed")
    target["schema"] = "sft-v3-postseal-complete-target-vector-correction/2"
    target["preserved_predecessor"] = (str(V1_TARGET.relative_to(ROOT)), V1_TARGET_HASH)
    target["correction_scope"] = (
        "One uppercase HTML closing-tag boundary in the separated-double-bond control; "
        "no source, identity, law, prediction, role or other target row changed."
    )
    write_json(V2_TARGET, target)

    analysis = primary["exact_postseal_analysis"]
    corrected_row = next(row for row in target["rows"] if row["source_record_role"] == CORRECTED_ROLE)
    control = corrected_row["source_outcome"]
    analysis["separated_control_internal_coordinate_rows"] = len(control["complete_internal_coordinate_table"]) - 2
    analysis["separated_control_bond_description_rows"] = len(control["complete_bond_description_table"]) - 1
    analysis["external_signed_control_inscription_preserved"] = any(
        cell.startswith("-") for row in control["complete_internal_coordinate_table"] for cell in row
    )
    analysis["complete_target_vector_hash"] = sha256_identity(
        tuple((row["target_id"], row["source_outcome"]) for row in target["rows"])
    )
    analysis["preserved_v1_parser_overrun_count"] = 1
    analysis["v2_corrected_table_count"] = 2
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
