#!/usr/bin/env python3
"""Build post-law-seal INORG-008 definitions and shared absorption vector."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


LAW_PATH = "sft/chemistry/inorganic_colour_transition_law_v1.py"
LAW_HASH = "sha256:b0c83c8c6c025bf61f31e33cda54a74675ec8ac2d89e9b800639f329372480bf"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_008_absorption_shared_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:e6719491d5f20147bbded3f849ba3aa71bcb6d4d201e485e87ecd102496bb319"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorganic_colour_transition_target_identities_v1.json"
IDENTITY_HASH = "sha256:104256d68f89a5573c8ba529787405e1279bc03132519894228f31c9d94d9b4f"
SHARED_TARGET_PATH = "experiments/external_sources/chemistry/ligand_state_splitting_withheld_targets_v1.json"
SHARED_TARGET_HASH = "sha256:2a843c7924c4f332c60c72dbb6338f9284fff6674d5f1ad76619388218c0d554"
TARGET_PATH = "experiments/external_sources/chemistry/inorganic_colour_transition_withheld_targets_v1.json"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorganic-colour-transition-primary-records-v1.json"
SHARED_TARGET_IDS = (
    "SFT-CHEM-INORG006-SPLIT-014", "SFT-CHEM-INORG006-SPLIT-020",
    "SFT-CHEM-INORG006-SPLIT-026", "SFT-CHEM-INORG006-SPLIT-032",
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    for path, expected in (
        (LAW_PATH, LAW_HASH), (ADDENDUM_PATH, ADDENDUM_HASH),
        (IDENTITY_PATH, IDENTITY_HASH), (SHARED_TARGET_PATH, SHARED_TARGET_HASH),
    ):
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"INORG-008 sealed input changed: {path}")
    identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
    identities = identity_document["rows"]
    if len(identities) != 8 or identity_document["target_values_definitions_peak_positions_intensities_band_counts_outcomes_or_payload_hashes_present"] is not False:
        raise SystemExit("INORG-008 identity boundary is not complete and value-free")
    for row in identities:
        if hash_file(ROOT / row["snapshot_path"]) != row["snapshot_sha256"]:
            raise SystemExit(f"INORG-008 registered source changed: {row['source_id']}")

    definition_outcomes = []
    for row in identities[:4]:
        source = json.loads((ROOT / row["snapshot_path"]).read_text(encoding="utf-8"))["term"]
        text = source["definitions"][0]["text"]
        definition_outcomes.append({
            "observed_source_code": source["code"],
            "observed_title": source["title"],
            "definition": text,
            "two_distinct_electronic_levels_present": "from an electronic energy level" in text and "to another energy level" in text,
            "ligand_to_ligand_endpoint_surface_present": "between two ligands" in text,
            "ligand_to_metal_endpoint_surface_present": "from a ligand to a metal centre" in text,
            "metal_to_ligand_endpoint_surface_present": "from the metal to a ligand" in text,
            "dimensional_spectrum_values_present": False,
        })

    shared = json.loads((ROOT / SHARED_TARGET_PATH).read_text(encoding="utf-8"))["rows"]
    shared_by_id = {row["target_id"]: row for row in shared}
    spectrum_outcomes = []
    for target_id in SHARED_TARGET_IDS:
        row = shared_by_id[target_id]
        outcome = row["source_outcome"]
        if outcome.get("payload_class") != "complete-uv-visible-spectrum":
            raise SystemExit(f"INORG-008 shared target is not a complete spectrum: {target_id}")
        spectrum_outcomes.append({
            **outcome,
            "shared_prior_target_id": target_id,
            "shared_prior_target_payload_hash": row["target_payload_hash"],
            "source_recaptured_for_inorg_008": False,
        })

    outcomes = tuple(definition_outcomes) + tuple(spectrum_outcomes)
    target_rows = []
    for identity, outcome in zip(identities, outcomes):
        row = {**identity, "source_outcome": outcome}
        row["target_payload_hash"] = sha256_identity((identity["target_id"], identity["source_record_role"], outcome))
        target_rows.append(row)
    target_document = {
        "schema": "sft-v3-chemistry-inorganic-colour-transition-withheld-targets/1",
        "claim_id": "SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008",
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "shared_admitted_evidence": {"path": SHARED_TARGET_PATH, "sha256": SHARED_TARGET_HASH},
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": 8,
        "all_definition_development_and_originally_blind_rows_preserved": True,
        "rows": target_rows,
    }
    write_json(ROOT / TARGET_PATH, target_document)

    maxima = [tuple(peak["x"] for peak in row["complete_interior_local_maxima"]) for row in spectrum_outcomes]
    point_counts = [row["exact_point_count"] for row in spectrum_outcomes]
    primary = {
        "schema": "sft-v3-chemistry-inorganic-colour-transition-primary/1",
        "claim_id": "SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008",
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "complete_target_count": 8,
        "exact_postseal_analysis": {
            "forced_directed_carrier_class_vector": ["ligand-to-ligand", "ligand-to-metal", "metal-to-ligand", "metal-to-metal"],
            "iupac_observed_transition_class_vector": ["generic", "ligand-to-ligand", "ligand-to-metal", "metal-to-ligand"],
            "metal_to_metal_definition_surface_absent_from_frozen_family": True,
            "complete_spectrum_count": 4,
            "complete_point_count_vector": point_counts,
            "complete_total_point_count": sum(point_counts),
            "complete_interior_maximum_count_vector": [len(row) for row in maxima],
            "complete_interior_maximum_position_vector_nm": maxima,
            "every_complete_spectrum_has_positive_selective_maximum_support": all(row for row in maxima),
            "original_custody_class_vector": [row["custody_class"] for row in identities[4:]],
            "originally_law_sealed_blind_spectrum_count": sum("originally-law-sealed-blind" in row["custody_class"] for row in identities[4:]),
            "source_recapture_count": 0,
            "dimensional_wavelength_intensity_or_colour_name_fitted_or_derived": False,
            "all_eight_rows_preserved": True,
        },
    }
    write_json(ROOT / PRIMARY_PATH, primary)
    print(hash_file(ROOT / TARGET_PATH))
    print(hash_file(ROOT / PRIMARY_PATH))


if __name__ == "__main__":
    main()
