#!/usr/bin/env python3
"""Open and preserve the complete INORG-004 vector after identity sealing."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITIES = ROOT / "experiments/external_sources/chemistry/coordination_geometry_target_identities_v1.json"
IDENTITIES_HASH = "sha256:8b93d120cebb9b4c26015f566fbbccdd6a04804e94e69b55264bf779ecd2554c"
CORRECTION = ROOT / "experiments/external_sources/chemistry/inorg_004_geometry_identity_correction_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/coordination_geometry_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/coordination-geometry-primary-records-v1.json"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def plain(fragment: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(value).split())


def between(text: str, start: str, end: str) -> str:
    match = re.search(start + r"(.*?)" + end, text, re.I | re.S)
    return match.group(1) if match else ""


def heading(text: str) -> str:
    return plain(between(text, r"<H1[^>]*>", r"</H1>"))


def point_group(text: str) -> str:
    value = plain(between(text, r"<H2>Point Group", r"</H2>"))
    return value


def table_after(text: str, label_pattern: str) -> str:
    match = re.search(label_pattern + r".*?(<table\b.*?</table>)", text, re.I | re.S)
    return plain(match.group(1)) if match else ""


def bond_rows(text: str) -> tuple[tuple[str, str], ...]:
    block = between(text, r"<h2>Bond descriptions</h2>", r"</TABLE>")
    rows = []
    for row in re.findall(r"<TR>(.*?)</TR>", block, re.I | re.S):
        cells = [plain(cell) for cell in re.findall(r"<T[DH][^>]*>(.*?)</T[DH]>", row, re.I | re.S)]
        if len(cells) >= 2 and cells[0] != "Bond Type":
            rows.append((cells[0], cells[1]))
    return tuple(rows)


def cartesian_surface(text: str) -> str:
    for block in re.findall(r"<table\b.*?</table>", text, re.I | re.S):
        header = plain(block[:1000])
        if "Atom" in header and "x (Å)" in header and "y (Å)" in header and "z (Å)" in header:
            return plain(block)
    return ""


def reference_absence_surface(text: str) -> dict:
    reference = between(text, r"<div class=\"box\" title=\"References\">", r"</div>")
    absence = tuple(sorted(set(re.findall(r"No experimental [^.<\r\n]+", text, re.I))))
    return {"reference_surface": plain(reference), "absence_statuses": absence}


def source_surface(identity: dict, text: str, correction: dict) -> object:
    role = identity["source_record_role"]
    path = ROOT / identity["snapshot_path"]
    source_id = identity["source_id"]
    if source_id == "IUPAC-C01332":
        term = json.loads(text)["term"]
        if role == "complete-source-file":
            return hash_file(path)
        if role == "complete-definition-surface":
            return term.get("definitions", [])
        if role == "term-identity-and-status":
            return {key: term.get(key) for key in ("id", "title", "code", "status")}
        if role == "source-citation-license-disclaimer-surface":
            return {
                "sources": [row.get("sources", []) for row in term.get("definitions", [])],
                "citation": term.get("citation"),
                "license": term.get("license"),
                "disclaimer": term.get("disclaimer"),
            }
    if source_id in correction["original_adverse_source_ids"]:
        declared = identity["source_document_identity"]
        observed = heading(text)
        if role == "declared-target-identity":
            return declared
        if role == "complete-response-file":
            return hash_file(path)
        if role == "identity-correspondence-status":
            return {
                "declared_identity": declared,
                "observed_source_entity": observed,
                "status": "adverse-target-identity-mismatch" if "Formaldehyde" in observed else "identity-not-proven",
            }
    if source_id == "NIST-CCCBDB-ALL-SPECIES-IDENTITY-LIST":
        if role == "complete-source-file":
            return hash_file(path)
        if role == "five-selected-target-identity-rows":
            selected = []
            for row in correction["sources"][1:]:
                cas = re.search(r"casno=(\d+)", row["uri"]).group(1)
                match = re.search(rf"<a href=\"alldata2x\.asp\?casno={cas}&amp;charge=0\">(.*?)</a>", text, re.I | re.S)
                selected.append({"source_id": row["source_id"], "cas_digits": cas, "list_identity": plain(match.group(1)) if match else "source-row-absent"})
            return selected
    if role == "complete-response-file":
        return hash_file(path)
    if role == "source-entity-identity":
        return heading(text)
    if role == "point-group-inscription":
        return point_group(text)
    if role == "direct-bond-count-surface":
        return bond_rows(text)
    if role == "internal-coordinate-surface":
        return table_after(text, r"<H2>Internal coordinates</H2>")
    if role == "cartesian-coordinate-surface":
        return cartesian_surface(text)
    if role == "reference-and-absence-status-surface":
        return reference_absence_surface(text)
    raise ValueError(f"unrecognized INORG-004 source surface: {source_id} {role}")


def main() -> None:
    if hash_file(IDENTITIES) != IDENTITIES_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-004 target identities changed")
    identities = json.loads(IDENTITIES.read_text(encoding="utf-8"))
    if identities.get("target_values_or_payload_hashes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: INORG-004 identity document contains target values")
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    rows = []
    for identity in identities["rows"]:
        text = (ROOT / identity["snapshot_path"]).read_text(encoding="utf-8", errors="replace")
        inscription = source_surface(identity, text, correction)
        rows.append(
            identity
            | {
                "source_inscription": inscription,
                "target_payload_hash": sha256_identity((identity["target_id"], identity["source_record_role"], inscription)),
                "status": "reported-authoritative-record" if identity["source_id"] not in correction["original_adverse_source_ids"] else "preserved-adverse-target-identity-record",
            }
        )
    targets = {
        "schema": "sft-v3-coordination-geometry-withheld-targets/1",
        "identity_document_sha256": IDENTITIES_HASH,
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "rows": rows,
    }
    TARGETS.write_text(json.dumps(targets, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    by_source = {}
    for row in rows:
        by_source.setdefault(row["source_id"], {})[row["source_record_role"]] = row["source_inscription"]
    corrected_sources = correction["sources"][1:]
    positive_words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    geometry_vector = []
    for source in corrected_sources:
        surfaces = by_source[source["source_id"]]
        declared_word = next(word for word in positive_words if source["identity"].endswith(word))
        declared_count = positive_words[declared_word]
        bond_counts = tuple(int(count) for _, count in surfaces["direct-bond-count-surface"] if count.isdigit())
        geometry_vector.append(
            {
                "source_id": source["source_id"],
                "declared_positive_incidence_count": declared_count,
                "source_entity_identity": surfaces["source-entity-identity"],
                "source_point_group_inscription": surfaces["point-group-inscription"],
                "source_direct_bond_rows": surfaces["direct-bond-count-surface"],
                "source_internal_coordinate_surface": surfaces["internal-coordinate-surface"],
                "source_cartesian_coordinate_surface": surfaces["cartesian-coordinate-surface"],
                "source_reference_and_absence_status_surface": surfaces["reference-and-absence-status-surface"],
                "direct_count_correspondence": declared_count in bond_counts,
            }
        )
    definition_text = canonical(by_source["IUPAC-C01332"]["complete-definition-surface"])
    adverse = [
        by_source[source_id]["identity-correspondence-status"]
        for source_id in correction["original_adverse_source_ids"]
    ]
    analysis = {
        "iupac_direct_ligand_position_central_relation_retained": all(fragment in definition_text for fragment in ("positions of the ligand atoms", "directly attached", "central atom")),
        "all_original_target_identity_mismatches_preserved": len(adverse) == 4 and all(row["status"] == "adverse-target-identity-mismatch" for row in adverse),
        "all_corrected_source_identities_retained": len(geometry_vector) == 5 and all("Listing of experimental geometry data for" in row["source_entity_identity"] for row in geometry_vector),
        "positive_direct_incidence_counts_two_through_six_retained": tuple(row["declared_positive_incidence_count"] for row in geometry_vector) == (2, 3, 4, 5, 6) and all(row["direct_count_correspondence"] for row in geometry_vector),
        "all_point_group_inscriptions_retained_without_shape_selection": all(row["source_point_group_inscription"] for row in geometry_vector),
        "all_coordinate_surfaces_preserved_including_reported_absence": all(
            isinstance(row["source_internal_coordinate_surface"], str)
            and isinstance(row["source_cartesian_coordinate_surface"], str)
            for row in geometry_vector
        ),
        "all_reference_and_absence_status_surfaces_retained": all(
            row["source_reference_and_absence_status_surface"]["reference_surface"]
            or row["source_reference_and_absence_status_surface"]["absence_statuses"]
            for row in geometry_vector
        ),
        "all_fifty_three_target_surfaces_retained": len(rows) == 53,
    }
    if not all(analysis.values()):
        raise SystemExit(f"INORG-004 complete authoritative surface changed: {analysis}")
    primary = {
        "schema": "sft-v3-coordination-geometry-primary-records/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-004",
        "claim_id": "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
        "identity_document_sha256": IDENTITIES_HASH,
        "target_document_sha256": hash_file(TARGETS),
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": {"IUPAC": 4, "NIST-CCCBDB-original-adverse": 12, "NIST-CCCBDB-identity-list": 2, "NIST-CCCBDB-corrected-geometry": 35},
        "exact_postseal_analysis": analysis,
        "complete_corrected_geometry_vector": geometry_vector,
        "complete_original_adverse_identity_vector": adverse,
        "coordination_count_alone_used_to_select_geometry": False,
        "point_group_shape_angle_distance_or_coordinate_used_as_fold_proof_parameter": False,
        "rows": rows,
    }
    PRIMARY.write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "targets_sha256": hash_file(TARGETS), "primary_sha256": hash_file(PRIMARY)}, sort_keys=True))


if __name__ == "__main__":
    main()
