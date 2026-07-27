#!/usr/bin/env python3
"""Preserve INORG-016 V1 and include registered source-note surfaces in V2.

The shared INORG-014--017 builder searched title, synonym and definition text.
Two already registered INORG-016 identities point instead to complete source-note
surfaces.  This versioned, claim-specific correction preserves the V1 target and
primary records byte-for-byte and changes no identity, source, role or phrase.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/inorg_016_target_identities_v1.json"
V1_TARGET_PATH = ROOT / "experiments/external_sources/chemistry/inorg_016_withheld_targets_v1.json"
V1_PRIMARY_PATH = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-016-primary-records-v1.json"
V2_TARGET_PATH = ROOT / "experiments/external_sources/chemistry/inorg_016_withheld_targets_v2.json"
V2_PRIMARY_PATH = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-016-primary-records-v2.json"
IDENTITY_HASH = "sha256:f2f97dc76295f1007d6cc6868080129839ff0e1b9d5e3f0b757092e0086f3328"
V1_TARGET_HASH = "sha256:c170a932926c96fb479ae43777663db2e865a3e64f83ff4cb28c5ce4a667c3cd"
V1_PRIMARY_HASH = "sha256:ecec2d5bc15b307013c8a53b805dd373abb9cc6016b6b30c5c4d542acaf3cdba"
NOTE_ROLES = {
    "surface-and-near-surface-bulk-role": "bulk defects located in the near-surface region",
    "vacancy-interstitial-edge-corner-kink-examples": "Surface vacancies",
}


def main() -> None:
    for path, expected in (
        (IDENTITY_PATH, IDENTITY_HASH),
        (V1_TARGET_PATH, V1_TARGET_HASH),
        (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
    ):
        if hash_file(path) != expected:
            raise SystemExit(f"INORG-016 predecessor changed: {path.relative_to(ROOT)}")
    identity = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    predecessor = json.loads(V1_TARGET_PATH.read_text(encoding="utf-8"))
    predecessor_by_target = {row["target_id"]: row for row in predecessor["rows"]}
    rows = []
    corrected_roles = []
    for registered in identity["rows"]:
        row = dict(predecessor_by_target[registered["target_id"]])
        role = registered["source_record_role"]
        if role in NOTE_ROLES:
            source = json.loads((ROOT / registered["snapshot_path"]).read_text(encoding="utf-8"))["term"]
            definition = source["definitions"][0]
            notes = tuple(str(value) for _, value in sorted(definition.get("notes", {}).items()))
            phrase = NOTE_ROLES[role]
            matching_notes = tuple(note for note in notes if phrase.casefold() in note.casefold())
            if len(matching_notes) != 1:
                raise SystemExit(f"INORG-016 registered note surface is not unique: {role}")
            outcome = dict(row["source_outcome"])
            outcome["complete_source_note_text"] = matching_notes[0]
            outcome["registered_surface_present"] = True
            outcome["surface_location"] = "definition-note"
            row["source_outcome"] = outcome
            row["target_payload_hash"] = sha256_identity(
                (registered["target_id"], role, outcome)
            )
            corrected_roles.append(role)
        rows.append(row)
    if tuple(corrected_roles) != tuple(NOTE_ROLES):
        raise SystemExit("INORG-016 correction did not cover exactly the registered note roles")
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/2",
        "claim_id": identity["claim_id"],
        "identity_registry": (str(IDENTITY_PATH.relative_to(ROOT)), IDENTITY_HASH),
        "preserved_predecessor_target": (str(V1_TARGET_PATH.relative_to(ROOT)), V1_TARGET_HASH),
        "preserved_predecessor_primary": (str(V1_PRIMARY_PATH.relative_to(ROOT)), V1_PRIMARY_HASH),
        "correction_scope": "two preregistered surfaces occur in complete definition notes rather than definition text",
        "corrected_registered_roles": tuple(corrected_roles),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "rows": rows,
    }
    V2_TARGET_PATH.write_text(
        json.dumps(target, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    analysis = {
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "all_registered_surfaces_present": all(
            row["source_outcome"]["registered_surface_present"] for row in rows
        ),
        "development_observed_target_count": sum(
            "development-observed" in row["custody_class"] for row in rows
        ),
        "identity_only_unopened_target_count": sum(
            "identity-only-unopened" in row["custody_class"] for row in rows
        ),
        "scope_mismatch_or_distinction_count": sum(
            "scope" in row["source_record_role"] or "returned" in row["source_record_role"]
            for row in rows
        ),
        "definition_note_surface_count": len(corrected_roles),
        "rendered_structure_absence_count": 0,
        "complete_target_vector_hash": sha256_identity(
            tuple((row["target_id"], row["source_outcome"]) for row in rows)
        ),
        "source_recapture_count": 0,
        "all_rows_preserved": True,
    }
    primary = {
        "schema": "sft-v3-postseal-primary-analysis/2",
        "claim_id": identity["claim_id"],
        "identity_registry": (str(IDENTITY_PATH.relative_to(ROOT)), IDENTITY_HASH),
        "preserved_predecessor_target": (str(V1_TARGET_PATH.relative_to(ROOT)), V1_TARGET_HASH),
        "preserved_predecessor_primary": (str(V1_PRIMARY_PATH.relative_to(ROOT)), V1_PRIMARY_HASH),
        "target_registry": (str(V2_TARGET_PATH.relative_to(ROOT)), hash_file(V2_TARGET_PATH)),
        "exact_postseal_analysis": analysis,
    }
    V2_PRIMARY_PATH.write_text(
        json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(V2_TARGET_PATH.relative_to(ROOT), hash_file(V2_TARGET_PATH))
    print(V2_PRIMARY_PATH.relative_to(ROOT), hash_file(V2_PRIMARY_PATH))
    print(json.dumps(analysis, sort_keys=True))


if __name__ == "__main__":
    main()
