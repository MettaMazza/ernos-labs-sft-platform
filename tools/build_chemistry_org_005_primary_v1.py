#!/usr/bin/env python3
"""Preserve the complete ORG-005 development-observed source surface."""
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


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_005_target_identities_v1.json"
IDENTITY_HASH = "sha256:7f148f0b99d0939aefb6023521d697dc00386a0de2f7a328d6b1220377965ad4"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_005_conformer_generation_equivalence_pre_source.json"
PREDICTION_PAYLOAD_HASH = "sha256:1af4780a78bb418650ac93f057ca51b907333213a51cb00a0307699d22fff6ff"
FAMILY_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:8b35e1f37dbf80713c47404d946a320da8d7011deaa5dbee7fe8393b58793cee"
TARGET = ROOT / "experiments/external_sources/chemistry/org_005_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-005-primary-records-v1.json"


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def parse_tables(raw: str) -> list[list[list[str]]]:
    tables = []
    for table in re.findall(r"<table\b[^>]*>(.*?)</table>", raw, flags=re.I | re.S):
        rows = []
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.I | re.S):
            cells = [text_only(cell) for cell in re.findall(r"<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>", row, flags=re.I | re.S)]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def cccbdb_surface(raw: str) -> dict:
    start = re.search(r"<h1[^>]*>Experimental data for", raw, flags=re.I)
    if not start:
        raise ValueError("ORG-005 CCCBDB experimental heading absent")
    section = raw[start.start():]
    heading = re.search(r"<h1[^>]*>(.*?)</h1>", section, flags=re.I | re.S)
    tables = parse_tables(section)
    if not heading or not tables:
        raise ValueError("ORG-005 CCCBDB complete surface absent")
    return {
        "returned_experimental_data_heading": text_only(heading.group(1)),
        "complete_experimental_data_tables": tables,
        "complete_table_count": len(tables),
        "complete_row_count": sum(len(table) for table in tables),
    }


def table(surface: dict, header: tuple[str, ...]) -> list[list[str]]:
    matches = [
        rows for rows in surface["complete_experimental_data_tables"]
        if rows and tuple(rows[0][: len(header)]) == header
    ]
    if len(matches) != 1:
        raise ValueError(f"ORG-005 table cardinality changed: {header}")
    return matches[0]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if TARGET.exists() or PRIMARY.exists():
        raise SystemExit("ORG-005 complete target surface already exists; preserved without replay")
    if hash_file(IDENTITY) != IDENTITY_HASH or hash_file(FAMILY_INVENTORY) != FAMILY_INVENTORY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 identity or family inventory changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 observational seal changed")
    identity_document = json.loads(IDENTITY.read_text(encoding="utf-8"))
    identities = identity_document.get("rows", [])
    if (
        identity_document.get("complete_registered_target_count") != 4
        or identity_document.get("development_observed_target_count") != 4
        or identity_document.get("outcome_unopened_blind_target_count") != 0
        or identity_document.get(
            "target_definitions_returned_states_conformations_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
        ) is not False
        or len(identities) != 4
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 identity census changed")
    released = []
    by_role = {}
    for item in identities:
        path = ROOT / item["snapshot_path"]
        if hash_file(path) != item["snapshot_sha256"]:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-005 source changed: {path}")
        if item["authority"] == "IUPAC":
            outcome = {"complete_term_record": json.loads(path.read_text(encoding="utf-8"))["term"]}
        else:
            outcome = cccbdb_surface(path.read_text(encoding="utf-8", errors="replace"))
            outcome.update({"complete_snapshot_sha256": item["snapshot_sha256"], "complete_snapshot_byte_count": path.stat().st_size})
        row = {**item, "opened_snapshot_path": item["snapshot_path"], "opened_snapshot_sha256": item["snapshot_sha256"]}
        row["source_outcome"] = outcome
        row["target_payload_hash"] = sha256_identity((item["target_id"], item["source_record_role"], outcome))
        released.append(row)
        by_role[item["source_record_role"]] = outcome

    conformer_text = json.dumps(by_role["complete-conformer-term-record"]["complete_term_record"], ensure_ascii=False, sort_keys=True)
    conformation_text = json.dumps(by_role["complete-conformation-term-record"]["complete_term_record"], ensure_ascii=False, sort_keys=True)
    analysis_text = json.dumps(by_role["complete-conformational-analysis-term-record"]["complete_term_record"], ensure_ascii=False, sort_keys=True)
    butane = by_role["complete-butane-conformer-census-and-experimental-surface"]
    conformation_rows = table(butane, ("State", "Conformation"))
    state_rows = table(butane, ("State", "Config", "State description", "Conf description", "Exp. min.", "Dipole (Debye)"))
    property_rows = table(butane, ("Property", "Value", "Uncertainty", "units"))
    reference_rows = table(butane, ("squib", "reference", "DOI"))
    returned_classes = tuple(dict.fromkeys(row[3] for row in state_rows[2:]))
    if returned_classes != ("Anti", "Gauche"):
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 complete conformer class vector changed")
    anti_rows = [row for row in state_rows[2:] if row[3] == "Anti"]
    gauche_rows = [row for row in state_rows[2:] if row[3] == "Gauche"]
    barrier_rows = [row for row in property_rows[1:] if row[0] == "Barrier to Internal Rotation"]
    if (
        conformation_rows[1][1] != "Anti"
        or len(anti_rows) != 1
        or len(gauche_rows) != 1
        or anti_rows[0][4] != "True"
        or gauche_rows[0][4] != "False"
        or len(barrier_rows) != 1
        or barrier_rows[0][1] != "16.6"
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 experimental state or adverse row changed")
    if not any("gauche butane conformer" in " ".join(row).casefold() for row in reference_rows):
        raise SystemExit("VOID_INVALID_HALTED: ORG-005 gauche conformer reference absent")
    exact_analysis = {
        "complete_target_count": len(released),
        "complete_source_count": len({row["source_id"] for row in released}),
        "development_observed_target_count": 4,
        "outcome_unopened_blind_target_count": 0,
        "conformer_distinct_potential_energy_minimum_surface_present": "distinct potential energy minimum" in conformer_text,
        "conformation_single_bond_rotation_surface_present": "rotations about formally single bonds" in conformation_text,
        "conformational_analysis_relative_energy_surface_present": "relative energies" in analysis_text and "alternative conformations" in analysis_text,
        "returned_small_molecule_heading": butane["returned_experimental_data_heading"],
        "complete_external_conformer_class_labels": list(returned_classes),
        "complete_external_conformer_class_count": len(returned_classes),
        "external_primary_conformation_label": conformation_rows[1][1],
        "external_anti_exp_minimum_string": anti_rows[0][4],
        "external_gauche_exp_minimum_string": gauche_rows[0][4],
        "external_gauche_adverse_false_row_preserved": gauche_rows[0][4] == "False",
        "external_gauche_reference_present": True,
        "external_internal_rotation_barrier_strings": barrier_rows[0][1:4],
        "cccbdb_complete_table_count": butane["complete_table_count"],
        "cccbdb_complete_row_count": butane["complete_row_count"],
        "all_signed_zero_absent_favourable_adverse_and_unresolved_external_inscriptions_preserved": True,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in released)),
    }
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/1",
        "claim_id": identity_document["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "observational_derivation_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "family_source_inventory": (str(FAMILY_INVENTORY.relative_to(ROOT)), FAMILY_INVENTORY_HASH),
        "all_rows_development_observed_and_not_claimed_blind": True,
        "release_requires_derivation_seal": True,
        "complete_registered_target_count": len(released),
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "rows": released,
    }
    write_json(TARGET, target)
    primary = {
        "schema": "sft-v3-postseal-primary-analysis/1",
        "claim_id": identity_document["claim_id"],
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
