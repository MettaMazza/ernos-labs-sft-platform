#!/usr/bin/env python3
"""Open the complete ORG-002 authority records after prediction sealing."""

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
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_002_resonance_equivalence_pre_source.json"
PREDICTION_PAYLOAD_HASH = "sha256:8e17d81cb943624e2778dd9536017265534e1166791d4794ea58d034b5f2cc9e"
TARGET = ROOT / "experiments/external_sources/chemistry/org_002_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-002-primary-records-v1.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if TARGET.exists() or PRIMARY.exists():
        raise SystemExit("ORG-002 target surface already exists; preserved without replay")
    if hash_file(IDENTITY) != IDENTITY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-002 identities changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-002 prediction seal changed")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    rows = identity.get("rows", [])
    if (
        identity.get("complete_registered_target_count") != 4
        or identity.get(
            "target_definitions_notes_examples_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 4
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-002 identity census changed")
    released = []
    searchable = {}
    for item in rows:
        path = ROOT / item["snapshot_path"]
        if hash_file(path) != item["snapshot_sha256"]:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-002 source changed: {path}")
        term = json.loads(path.read_text(encoding="utf-8"))["term"]
        outcome = {
            "complete_term_record": term,
            "source_code": term["code"],
            "source_title": term["title"],
            "source_status": term["status"],
        }
        row = {**item, "source_outcome": outcome}
        row["target_payload_hash"] = sha256_identity(
            (item["target_id"], item["source_record_role"], outcome)
        )
        released.append(row)
        searchable[item["source_record_role"]] = json.dumps(term, sort_keys=True, ensure_ascii=False)
    resonance = searchable["complete-resonance-record"]
    form = searchable["complete-resonance-form-record"]
    contributing = searchable["complete-contributing-structure-record"]
    delocalization = searchable["complete-delocalization-correspondence-record"]
    analysis = {
        "complete_target_count": len(released),
        "complete_source_count": len({row["source_id"] for row in released}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed" for row in released
        ),
        "predecessor_opened_target_count": sum(
            row["custody_class"] == "family-identity-opened-by-admitted-ORG-001" for row in released
        ),
        "one_molecular_entity_representation_surface_present": "representation of the electronic structure of a molecular entity" in resonance,
        "at_least_two_formal_structures_surface_present": "at least two Lewis structures" in form,
        "single_structure_insufficient_surface_present": "cannot be described by a single Lewis structure" in form,
        "formal_not_species_surface_present": "purely formal significance" in contributing,
        "not_equilibrium_surface_present": "must not be confused with the double arrow connecting species in equilibrium" in form,
        "nonlocal_support_surface_present": "not localized between two atoms" in delocalization,
        "external_wavefunction_and_coefficient_language_preserved": "wavefunction" in contributing and "coefficient" in contributing,
        "external_signed_charge_inscription_preserved": "^{-}" in contributing or "^{-}" in delocalization,
        "all_rows_preserved": True,
        "source_recapture_count": 0,
        "complete_target_vector_hash": sha256_identity(
            tuple((row["target_id"], row["source_outcome"]) for row in released)
        ),
    }
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/1",
        "claim_id": identity["claim_id"],
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
        "claim_id": identity["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "target_registry": (str(TARGET.relative_to(ROOT)), hash_file(TARGET)),
        "exact_postseal_analysis": analysis,
    }
    write_json(PRIMARY, primary)
    print(f"{TARGET.relative_to(ROOT)} {hash_file(TARGET)}")
    print(f"{PRIMARY.relative_to(ROOT)} {hash_file(PRIMARY)}")
    print(json.dumps(analysis, sort_keys=True))


if __name__ == "__main__":
    main()
