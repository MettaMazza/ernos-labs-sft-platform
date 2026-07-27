#!/usr/bin/env python3
"""Build the complete value-free/withheld cross-property source boundary for PROP-014.

All source identities are loaded, normalized only by an explicit identity field,
written and hashed before any withheld target file is opened.  Every row from
PROP-001 through PROP-013 is retained.  Exact formula identifiers join across
property families; rows lacking a lawful shared formula remain explicit
single-property custody rows rather than being guessed into a species group.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-014-cross-property-v1"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/cross_property_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/cross_property_withheld_targets_v1.json"
MANIFEST_PATH = OUT_DIR / "cross-property-source-manifest-v1.json"
SUMMARY_PATH = OUT_DIR / "cross-property-overlap-summary-v1.json"


FAMILIES = (
    ("PROP-001", "equilibrium-bond-length", "equilibrium_bond_length_target_identities_v1.json", "equilibrium_bond_length_withheld_targets_v1.json", "species"),
    ("PROP-002", "bond-dissociation-energy", "bond_dissociation_energy_target_identities_v1.json", "bond_dissociation_energy_withheld_targets_v1.json", "species"),
    ("PROP-003", "bond-angle", "bond_angle_target_identities_v1.json", "bond_angle_withheld_targets_v1.json", "species"),
    ("PROP-004", "dihedral-torsional-state", "dihedral_torsion_target_identities_v1.json", "dihedral_torsion_withheld_targets_v1.json", "species"),
    ("PROP-005", "molecular-dipole", "molecular_dipole_target_identities_v1.json", "molecular_dipole_withheld_targets_v1.json", "species"),
    ("PROP-006", "molecular-polarizability", "molecular_polarizability_target_identities_v1.json", "molecular_polarizability_withheld_targets_v1.json", "formula"),
    ("PROP-007", "molecular-ionization-energy", "molecular_ionization_target_identities_v1.json", "molecular_ionization_withheld_targets_v1.json", "formula"),
    ("PROP-008", "molecular-electron-affinity", "molecular_electron_affinity_target_identities_v1.json", "molecular_electron_affinity_withheld_targets_v1.json", "formula"),
    ("PROP-009", "vibrational-frequency", "vibrational_frequency_target_identities_v1.json", "vibrational_frequency_withheld_targets_v1.json", "formula"),
    ("PROP-010", "rotational-constant", "rotational_constant_target_identities_v1.json", "rotational_constant_withheld_targets_v1.json", "species"),
    ("PROP-011", "intermolecular-binding", "intermolecular_binding_target_identities_v1.json", "intermolecular_binding_withheld_targets_v1.json", "dimer_formula"),
    ("PROP-012", "molecular-magnetic-response", "magnetic_response_target_identities_v1.json", "magnetic_response_withheld_targets_v1.json", None),
    ("PROP-013", "molecular-formation-energy", "formation_energy_target_identities_v1.json", "formation_energy_withheld_targets_v1.json", "species"),
)


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hash(payload: object) -> str:
    return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def carrier_id(prop: str, identity: dict[str, object], field: str | None) -> tuple[str, str]:
    if prop == "PROP-012":
        locator = str(identity.get("source_locator", ""))
        if ".html" in locator:
            formula = PurePosixPath(urlparse(locator).path).stem
            if formula:
                return "exact-formula:" + formula, "formula-from-official-NIST-page-identity"
        return "unjoined-source-target:" + str(identity["target_id"]), "no-explicit-species-formula-in-registered-diatomic-PDF-cell"
    if prop == "PROP-004":
        return "source-species-label:" + str(identity[field]).strip(), "source-species-label-not-formula-normalized"
    if prop == "PROP-011":
        return "bound-composite-formula:" + str(identity[field]).strip(), "bound-composite-not-conflated-with-constituent-molecule"
    value = str(identity[field]).strip()
    if not value:
        return "unjoined-source-target:" + str(identity["target_id"]), "registered-identity-has-no-formula"
    return "exact-formula:" + value, "exact-registered-formula"


def main() -> None:
    base = ROOT / "experiments/external_sources/chemistry"
    identity_rows: list[dict[str, object]] = []
    source_manifest: list[dict[str, object]] = []
    source_identities: dict[str, tuple[dict[str, object], ...]] = {}

    # Phase one: values and target presence remain unopened.
    for prop, label, identity_name, target_name, field in FAMILIES:
        identity_path = base / identity_name
        document = json.loads(identity_path.read_text(encoding="utf-8"))
        rows = tuple(document.get("rows", ()))
        if not rows or len(rows) != len({str(row["target_id"]) for row in rows}):
            raise RuntimeError(f"{prop} identity registry is empty or duplicated")
        source_identities[prop] = rows
        source_manifest.append({
            "property_family": prop, "property_label": label,
            "identity_path": str(identity_path.relative_to(ROOT)), "identity_hash": sha256_file(identity_path),
            "identity_schema": document.get("schema"), "identity_row_count": len(rows),
            "withheld_target_path": str((base / target_name).relative_to(ROOT)),
            "withheld_target_hash_absent_until_identity_seal": True,
        })
        for ordinal, identity in enumerate(rows, start=1):
            carrier, rule = carrier_id(prop, identity, field)
            identity_rows.append({
                "cross_property_target_id": f"SFT-CHEM-PROP-014-{prop}-ROW-{ordinal:04d}",
                "structural_carrier_id": carrier,
                "carrier_derivation_rule": rule,
                "property_family": prop,
                "property_label": label,
                "source_target_id": str(identity["target_id"]),
                "source_identity_ordinal": ordinal,
                "source_identity_path": str(identity_path.relative_to(ROOT)),
                "source_identity_hash": canonical_hash(identity),
                "target_value_presence_and_orientation_absent": True,
            })

    family_by_carrier: dict[str, set[str]] = {}
    rows_by_carrier: dict[str, int] = {}
    for row in identity_rows:
        carrier = str(row["structural_carrier_id"])
        family_by_carrier.setdefault(carrier, set()).add(str(row["property_family"]))
        rows_by_carrier[carrier] = rows_by_carrier.get(carrier, 0) + 1
    for row in identity_rows:
        carrier = str(row["structural_carrier_id"])
        row["registered_property_family_count_for_carrier"] = len(family_by_carrier[carrier])
        row["complete_registered_row_count_for_carrier"] = rows_by_carrier[carrier]
        row["cross_property_overlap"] = len(family_by_carrier[carrier]) >= 2

    identity_document = {
        "schema": "sft-v3-cross-property-identities/1",
        "complete_property_family_count": len(FAMILIES),
        "complete_source_identity_row_count": len(identity_rows),
        "complete_structural_carrier_count": len(family_by_carrier),
        "multi_property_structural_carrier_count": sum(len(v) >= 2 for v in family_by_carrier.values()),
        "all_target_values_presence_flags_and_source_orientations_absent": True,
        "rows": identity_rows,
    }
    write_json(IDENTITY_PATH, identity_document)
    identity_seal = sha256_file(IDENTITY_PATH)
    write_json(MANIFEST_PATH, {
        "schema": "sft-v3-cross-property-source-manifest/1",
        "identity_seal_before_target_open": identity_seal,
        "complete_property_family_count": len(FAMILIES),
        "sources": source_manifest,
    })

    # Phase two: first target access occurs only after the complete identity seal.
    target_rows: list[dict[str, object]] = []
    target_file_manifest: list[dict[str, object]] = []
    identity_offset = 0
    for (prop, label, identity_name, target_name, field), manifest_row in zip(FAMILIES, source_manifest):
        targets_document = json.loads((base / target_name).read_text(encoding="utf-8"))
        target_file_manifest.append({
            "property_family": prop,
            "withheld_target_path": str((base / target_name).relative_to(ROOT)),
            "withheld_target_hash_first_read_after_identity_seal": sha256_file(base / target_name),
            "withheld_target_schema": targets_document.get("schema"),
        })
        targets = tuple(targets_document.get("rows", ()))
        identities = source_identities[prop]
        if len(targets) != len(identities):
            raise RuntimeError(f"{prop} identity/target cardinality differs")
        target_by_id = {str(row["target_id"]): row for row in targets}
        if len(target_by_id) != len(targets):
            raise RuntimeError(f"{prop} target registry is duplicated")
        for local_ordinal, identity in enumerate(identities):
            cross_identity = identity_rows[identity_offset + local_ordinal]
            source_target_id = str(identity["target_id"])
            if source_target_id not in target_by_id:
                raise RuntimeError(f"{prop} target identity missing: {source_target_id}")
            target_rows.append({
                "cross_property_target_id": cross_identity["cross_property_target_id"],
                "structural_carrier_id": cross_identity["structural_carrier_id"],
                "property_family": prop,
                "source_target_id": source_target_id,
                "source_target_payload": target_by_id[source_target_id],
                "source_target_payload_hash": canonical_hash(target_by_id[source_target_id]),
            })
        identity_offset += len(identities)

    write_json(TARGET_PATH, {
        "schema": "sft-v3-cross-property-withheld-targets/1",
        "release_requires_complete_identity_prediction_seal": True,
        "identity_seal": identity_seal,
        "complete_target_row_count": len(target_rows),
        "source_target_files_first_opened_after_identity_seal": target_file_manifest,
        "rows": target_rows,
    })
    family_counts = {prop: sum(row["property_family"] == prop for row in identity_rows) for prop, *_ in FAMILIES}
    overlap_family_counts = {
        prop: sum(row["property_family"] == prop and row["cross_property_overlap"] for row in identity_rows)
        for prop, *_ in FAMILIES
    }
    max_family_count = max(len(v) for v in family_by_carrier.values())
    leaders = sorted(
        ({"structural_carrier_id": carrier, "property_families": sorted(families), "property_family_count": len(families), "row_count": rows_by_carrier[carrier]} for carrier, families in family_by_carrier.items() if len(families) == max_family_count),
        key=lambda row: str(row["structural_carrier_id"]),
    )
    summary = {
        "schema": "sft-v3-cross-property-overlap-summary/1",
        "complete_identity_hash": identity_seal,
        "complete_target_hash": sha256_file(TARGET_PATH),
        "complete_source_identity_row_count": len(identity_rows),
        "complete_structural_carrier_count": len(family_by_carrier),
        "multi_property_structural_carrier_count": sum(len(v) >= 2 for v in family_by_carrier.values()),
        "multi_property_source_row_count": sum(bool(row["cross_property_overlap"]) for row in identity_rows),
        "complete_property_family_row_counts": family_counts,
        "multi_property_family_row_counts": overlap_family_counts,
        "maximum_property_family_count_on_one_carrier": max_family_count,
        "maximum_coverage_carriers": leaders,
        "nonjoined_rows_remain_explicit_and_are_not_assigned_by_guess": True,
    }
    write_json(SUMMARY_PATH, summary)
    print(json.dumps({
        "identity_hash": identity_seal, "target_hash": sha256_file(TARGET_PATH),
        "manifest_hash": sha256_file(MANIFEST_PATH), "summary_hash": sha256_file(SUMMARY_PATH),
        "property_families": len(FAMILIES), "source_rows": len(identity_rows),
        "structural_carriers": len(family_by_carrier),
        "multi_property_carriers": summary["multi_property_structural_carrier_count"],
        "multi_property_rows": summary["multi_property_source_row_count"],
        "maximum_property_families": max_family_count,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
