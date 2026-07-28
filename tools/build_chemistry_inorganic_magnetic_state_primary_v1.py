#!/usr/bin/env python3
"""Build post-law-seal INORG-009 definitions and complete shared NIST vector."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


LAW_PATH = "sft/chemistry/inorganic_magnetic_state_law_v1.py"
LAW_HASH = "sha256:27c299058fa6ec1489155395766f280e3cd6e29d0786828d0e75c2d0018e9452"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_009_magnetic_shared_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:b55fb12e09536da326158a016df2ccd028f4a0e8bb84ddb736a2252dbdbff161"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorganic_magnetic_state_target_identities_v1.json"
IDENTITY_HASH = "sha256:87f36708bf7712467fea1e08e9ca82464eb648c9d37f91fb10661694b7062555"
SHARED_TARGET_PATH = "experiments/external_sources/chemistry/magnetic_response_withheld_targets_v1.json"
SHARED_TARGET_HASH = "sha256:7ce119e64518c20376cdba0f1a8e0814ee76d48a6ee50acd562cfd4f44c8211d"
TARGET_PATH = "experiments/external_sources/chemistry/inorganic_magnetic_state_withheld_targets_v1.json"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorganic-magnetic-state-primary-records-v1.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    for path, expected in ((LAW_PATH, LAW_HASH), (ADDENDUM_PATH, ADDENDUM_HASH), (IDENTITY_PATH, IDENTITY_HASH), (SHARED_TARGET_PATH, SHARED_TARGET_HASH)):
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"INORG-009 sealed input changed: {path}")
    identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
    identities = identity_document["rows"]
    if len(identities) != 177 or identity_document["target_values_orientations_presence_flags_definitions_outcomes_or_payload_hashes_present"] is not False:
        raise SystemExit("INORG-009 identity vector is not complete and value-free")

    definition_outcomes = []
    for identity in identities[:3]:
        source = json.loads((ROOT / identity["snapshot_path"]).read_text(encoding="utf-8"))["term"]
        text = source["definitions"][0]["text"]
        definition_outcomes.append({
            "observed_source_code": source["code"], "observed_title": source["title"], "definition": text,
            "susceptibility_relative_permeability_relation_present": "Relative permeability minus one" in text,
            "paramagnetic_positive_external_sign_and_drawn_relation_present": "greater than 0" in text and "drawn into a magnetic field" in text,
            "diamagnetic_negative_external_sign_and_repelled_relation_present": "negative magnetic susceptibility" in text and "repelled out of a magnetic field" in text,
            "external_signed_inscription_retained_downstream_only": True,
        })
    shared = json.loads((ROOT / SHARED_TARGET_PATH).read_text(encoding="utf-8"))
    if shared.get("complete_target_count") != 174 or len(shared.get("rows", ())) != 174 or shared.get("release_requires_prediction_seal") is not True:
        raise SystemExit("INORG-009 shared target vector is incomplete")
    shared_by_id = {row["target_id"]: row for row in shared["rows"]}
    magnetic_outcomes = []
    for identity in identities[3:]:
        prior = shared_by_id[identity["shared_prior_target_id"]]
        magnetic_outcomes.append({
            "shared_prior_target_id": prior["target_id"],
            "source_value_present": prior["source_value_present"],
            "source_value_inscription": prior["source_value_inscription"],
            "native_value": prior["native_value"],
            "source_recaptured_for_inorg_009": False,
        })
    outcomes = tuple(definition_outcomes) + tuple(magnetic_outcomes)
    rows = []
    for identity, outcome in zip(identities, outcomes):
        row = {**identity, "source_outcome": outcome}
        row["target_payload_hash"] = sha256_identity((identity["target_id"], identity["source_record_role"], outcome))
        rows.append(row)
    target = {
        "schema": "sft-v3-chemistry-inorganic-magnetic-state-withheld-targets/1",
        "claim_id": "SFT-CHEM-INORGANIC-MAGNETIC-STATE-009",
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "shared_admitted_evidence": {"path": SHARED_TARGET_PATH, "sha256": SHARED_TARGET_HASH},
        "release_requires_prediction_seal": True, "complete_registered_target_count": 177,
        "all_definition_exact_magnitude_orientation_and_structural_absence_rows_preserved": True, "rows": rows,
    }
    write_json(ROOT / TARGET_PATH, target)

    present = [row for row in magnetic_outcomes if row["source_value_present"]]
    absent = [row for row in magnetic_outcomes if not row["source_value_present"]]
    orientations = Counter(
        row["native_value"].get("external_orientation", "structural-absence")
        if isinstance(row["native_value"], dict) else "structural-absence"
        for row in magnetic_outcomes
    )
    exact_magnitude_vector_hash = sha256_identity(tuple(row["native_value"] for row in magnetic_outcomes))
    primary = {
        "schema": "sft-v3-chemistry-inorganic-magnetic-state-primary/1",
        "claim_id": "SFT-CHEM-INORGANIC-MAGNETIC-STATE-009",
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "identity_registry": {"path": IDENTITY_PATH, "sha256": IDENTITY_HASH},
        "complete_target_count": 177,
        "exact_postseal_analysis": {
            "forced_balanced_state": {"moment_support": "EmptyOne", "spin_width": 1, "field_relation": "repelled-from-field", "magnetic_class": "diamagnetic"},
            "forced_four_unpaired_state": {"moment_support": 4, "spin_width": 5, "field_relation": "drawn-into-field", "magnetic_class": "paramagnetic"},
            "forced_unpaired_successor_state": {"moment_support": 5, "spin_width": 6, "field_relation": "drawn-into-field", "magnetic_class": "paramagnetic"},
            "complete_definition_count": 3, "complete_shared_magnetic_target_count": 174,
            "exact_positive_magnitude_count": len(present), "structural_absence_count": len(absent),
            "complete_orientation_class_counts": dict(sorted(orientations.items())),
            "complete_exact_magnitude_vector_hash": exact_magnitude_vector_hash,
            "source_recapture_count": 0,
            "square_root_spin_only_formula_fitted_g_factor_or_dimensional_moment_derived": False,
            "all_177_rows_preserved": True,
        },
    }
    write_json(ROOT / PRIMARY_PATH, primary)
    print(hash_file(ROOT / TARGET_PATH)); print(hash_file(ROOT / PRIMARY_PATH))


if __name__ == "__main__":
    main()
