#!/usr/bin/env python3
"""Open and preserve every ORG-001 target surface after prediction sealing."""

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
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_001_conjugated_support_pre_source.json"
PREDICTION_PAYLOAD_HASH = "sha256:0d5b02fc0add6291a0ca99f3564ffbd10e058735740f0b609bd229b45ccb778a"
TARGET = ROOT / "experiments/external_sources/chemistry/org_001_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-001-primary-records-v1.json"


IDENTITY_KEYS = (
    "target_id",
    "source_record_ordinal",
    "source_id",
    "authority",
    "registered_identity",
    "source_record_role",
    "custody_class",
    "snapshot_path",
    "snapshot_sha256",
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def text_only(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def table_after(raw: str, marker: str) -> list[list[str]]:
    position = raw.find(marker)
    if position < 0:
        raise ValueError(f"registered table marker absent: {marker}")
    start = raw.find("<table", position)
    end = raw.find("</table>", start)
    if start < 0 or end < 0:
        raise ValueError(f"registered table incomplete: {marker}")
    table = raw[start : end + len("</table>")]
    rows = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.I | re.S):
        cells = [
            text_only(cell)
            for cell in re.findall(r"<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>", row, flags=re.I | re.S)
        ]
        if cells:
            rows.append(cells)
    if not rows:
        raise ValueError(f"registered table has no rows: {marker}")
    return rows


def document_heading(raw: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", raw, flags=re.I | re.S)
    if not match:
        raise ValueError("registered NIST heading absent")
    return text_only(match.group(1))


def jcamp_record(raw: str) -> dict:
    headers: dict[str, str] = {}
    points: list[tuple[str, str]] = []
    in_points = False
    for source_line in raw.splitlines():
        line = source_line.strip()
        if not line:
            continue
        if line.startswith("##"):
            key, separator, value = line[2:].partition("=")
            headers[key] = value if separator else ""
            if key == "XYPOINTS":
                in_points = True
            continue
        if in_points and "," in line:
            left, right = line.split(",", 1)
            points.append((left.strip(), right.strip()))
    declared = int(headers["NPOINTS"])
    if declared != len(points):
        raise ValueError("complete JCAMP point count differs from declared point count")
    return {
        "headers": headers,
        "declared_point_count": declared,
        "complete_xy_point_strings": points,
    }


def iupac_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["term"]


def main() -> None:
    if TARGET.exists() or PRIMARY.exists():
        raise SystemExit("ORG-001 post-seal target surface already exists; preserved without replay")
    if hash_file(IDENTITY) != IDENTITY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 target identities changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 prediction seal changed")
    identities = json.loads(IDENTITY.read_text(encoding="utf-8"))
    rows = identities.get("rows", [])
    if (
        identities.get("complete_registered_target_count") != 10
        or identities.get(
            "target_definitions_coordinates_peaks_intensities_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 10
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 identity census changed")

    source_cache: dict[str, str] = {}
    iupac_cache: dict[str, dict] = {}
    outcomes: dict[str, dict] = {}
    for identity in rows:
        path = ROOT / identity["snapshot_path"]
        if hash_file(path) != identity["snapshot_sha256"]:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-001 source changed: {path}")
        role = identity["source_record_role"]
        if identity["authority"] == "IUPAC":
            term = iupac_cache.setdefault(str(path), iupac_record(path))
            definition = term["definitions"][0]
            outcomes[role] = {
                "source_code": term["code"],
                "source_title": term["title"],
                "source_status": term["status"],
                "complete_definition": definition,
                "complete_synonym_surface": term.get("synonym"),
                "complete_citation": term.get("citation"),
                "complete_licence": term.get("license"),
                "complete_disclaimer": term.get("disclaimer"),
            }
            continue
        raw = source_cache.setdefault(str(path), path.read_text(encoding="utf-8", errors="replace"))
        if role == "complete-conjugated-molecular-identity-surface":
            outcomes[role] = {
                "heading": document_heading(raw),
                "complete_identity_table": table_after(raw, '<table ID="idents">'),
                "complete_state_conformation_table": table_after(raw, '<table class="border">'),
            }
        elif role == "complete-conjugated-bond-and-coordinate-surface":
            outcomes[role] = {
                "complete_internal_coordinate_table": table_after(raw, '<br><span class="strong">Internal coordinates</span>'),
                "complete_bond_description_table": table_after(raw, '<p><span class="strong">Bond descriptions</span></p>'),
            }
        elif role == "complete-conjugated-vibrational-surface":
            outcomes[role] = {
                "complete_vibrational_table": table_after(raw, "Vibrational levels"),
            }
        elif role == "complete-separated-double-bond-control-identity":
            outcomes[role] = {
                "heading": document_heading(raw),
                "point_group_text": text_only(
                    re.search(r"<P><H2>Point Group(.*?)</H2>", raw, flags=re.I | re.S).group(1)
                ),
            }
        elif role == "complete-separated-double-bond-control-coordinate-surface":
            outcomes[role] = {
                "complete_internal_coordinate_table": table_after(raw, "<H2>Internal coordinates</H2>"),
                "complete_bond_description_table": table_after(raw, "<h2>Bond descriptions</h2>"),
            }
        elif role == "complete-uv-visible-spectrum-metadata-and-link-surface":
            uv_start = raw.find('<h2 id="UV-Vis-Spec">')
            refs = raw.find('<h2 id="Refs">', uv_start)
            if uv_start < 0 or refs < 0:
                raise ValueError("complete UV-visible metadata surface absent")
            uv_surface = raw[uv_start:refs]
            outcomes[role] = {
                "complete_uv_visible_surface_text": text_only(uv_surface),
                "jcamp_link_present": "JCAMP=C106990&amp;Index=0&amp;Type=UVVis" in uv_surface,
            }
        elif role == "complete-uv-visible-jcamp-point-surface":
            outcomes[role] = jcamp_record(raw)
        else:
            raise ValueError(f"unhandled ORG-001 role: {role}")

    released = []
    for identity in rows:
        outcome = outcomes[identity["source_record_role"]]
        row = {**identity, "source_outcome": outcome}
        row["target_payload_hash"] = sha256_identity(
            (identity["target_id"], identity["source_record_role"], outcome)
        )
        released.append(row)

    terms = [outcomes[name] for name in (
        "complete-conjugated-system-record",
        "complete-pi-conjugated-system-record",
        "complete-delocalization-record",
    )]
    term_texts = [
        item["complete_definition"]["text"] + " " + " ".join(item["complete_definition"].get("notes", {}).values())
        for item in terms
    ]
    conjugated_structure = outcomes["complete-conjugated-bond-and-coordinate-surface"]
    separated_control = outcomes["complete-separated-double-bond-control-coordinate-surface"]
    jcamp = outcomes["complete-uv-visible-jcamp-point-surface"]
    exact_analysis = {
        "complete_target_count": len(released),
        "complete_source_count": len({row["source_id"] for row in released}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed" for row in released
        ),
        "identity_only_unopened_target_count": sum(
            "identity-only-unopened" in row["custody_class"] for row in released
        ),
        "alternating_single_multiple_surface_count": sum(
            "alternating single and multiple bonds" in text for text in term_texts
        ),
        "connected_intervening_bond_surface_present": any(
            "across an intervening" in text for text in term_texts
        ),
        "delocalized_nonlocal_support_surface_present": any(
            "not localized between two atoms" in text for text in term_texts
        ),
        "conjugated_internal_coordinate_rows": len(conjugated_structure["complete_internal_coordinate_table"]) - 2,
        "conjugated_bond_description_rows": len(conjugated_structure["complete_bond_description_table"]) - 1,
        "separated_control_internal_coordinate_rows": len(separated_control["complete_internal_coordinate_table"]) - 2,
        "separated_control_bond_description_rows": len(separated_control["complete_bond_description_table"]) - 1,
        "complete_vibrational_table_rows": len(outcomes["complete-conjugated-vibrational-surface"]["complete_vibrational_table"]),
        "uv_visible_declared_point_count": jcamp["declared_point_count"],
        "uv_visible_preserved_point_count": len(jcamp["complete_xy_point_strings"]),
        "uv_visible_jcamp_link_present": outcomes["complete-uv-visible-spectrum-metadata-and-link-surface"]["jcamp_link_present"],
        "external_signed_control_inscription_preserved": any(
            cell.startswith("-")
            for row in separated_control["complete_internal_coordinate_table"]
            for cell in row
        ),
        "all_rows_preserved": True,
        "source_recapture_count": 0,
        "complete_target_vector_hash": sha256_identity(
            tuple((row["target_id"], row["source_outcome"]) for row in released)
        ),
    }
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/1",
        "claim_id": identities["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(released),
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "rows": released,
    }
    write_json(TARGET, target)
    primary = {
        "schema": "sft-v3-postseal-primary-analysis/1",
        "claim_id": identities["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "target_registry": (str(TARGET.relative_to(ROOT)), hash_file(TARGET)),
        "exact_postseal_analysis": exact_analysis,
    }
    write_json(PRIMARY, primary)
    print(f"{TARGET.relative_to(ROOT)} {hash_file(TARGET)}")
    print(f"{PRIMARY.relative_to(ROOT)} {hash_file(PRIMARY)}")
    print(json.dumps(exact_analysis, sort_keys=True))


if __name__ == "__main__":
    main()
