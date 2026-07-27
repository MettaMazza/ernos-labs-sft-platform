"""Registered exact state-order law and blind binding vector for Chemistry PROP-011."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.intermolecular_binding_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1"
INDEX_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-complete-hydrogen-bonded-dimer-list.html"
INDEX_HASH = "sha256:eaeeed87b43f4b250cb565b115f3f5b3a35e96990310a8da2644139c1f3ea206"
WATER_CLUSTER_PATH = f"{SNAPSHOT_ROOT}/nist-water-cluster-dissociation-values-2018.pdf"
WATER_CLUSTER_HASH = "sha256:f7e29beb17352ac54ad1188cee7677cb67b84507a3b32a3271b3a56a22b6d76c"
ION_CLUSTER_PATH = f"{SNAPSHOT_ROOT}/nist-ion-cluster-thermochemistry-complete-1986.pdf"
ION_CLUSTER_HASH = "sha256:ecddb4c3bca09d2f36508f2e95d4bf6a8737ea2443a971a9844de187e12bf990"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/intermolecular-binding-primary-records-v1.json"
PRIMARY_HASH = "sha256:41c1d6aa1b4ba2379f1eef8f99065c23c33723ff239b045d4aa5c046ac0c0b18"
IDENTITY_PATH = "experiments/external_sources/chemistry/intermolecular_binding_target_identities_v1.json"
IDENTITY_HASH = "sha256:cec8f404ba6c0d81c9473a5da033a056eea689d0cfd182247fb7ee972a46af47"
TARGET_PATH = "experiments/external_sources/chemistry/intermolecular_binding_withheld_targets_v1.json"
TARGET_HASH = "sha256:4dfc31201ba33de2b6ec139cd15669435a2bf4f282cef00d32e9d6523ff385b2"


for _path, _hash in (
    (INDEX_PATH, INDEX_HASH),
    (WATER_CLUSTER_PATH, WATER_CLUSTER_HASH),
    (ION_CLUSTER_PATH, ION_CLUSTER_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-011 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_forbidden = {
    "value_inscription_kJ_per_mol", "value_inscription_cm_inverse",
    "uncertainty_inscription_cm_inverse", "central_cm_inverse", "uncertainty_cm_inverse",
    "lower_cm_inverse", "upper_cm_inverse", "external_orientation",
    "absolute_inscribed_magnitude_kJ_per_mol",
}
if (
    _primary.get("schema") != "sft-v3-intermolecular-binding-primary-records/1"
    or _primary.get("complete_cccbdb_dimer_count") != 11
    or _primary.get("complete_cccbdb_linked_value_count") != 1297
    or _primary.get("complete_cccbdb_positive_value_count") != 1201
    or _primary.get("complete_cccbdb_signed_adverse_value_count") != 96
    or _primary.get("reported_experimental_cluster_dissociation_count") != 2
    or _identity_document.get("schema") != "sft-v3-intermolecular-binding-identities/1"
    or _identity_document.get("all_binding_values_absent") is not True
    or _identity_document.get("complete_row_count") != 1299
    or len(_identity_document.get("rows", ())) != 1299
    or not all(
        row.get("target_value_absent") is True
        and row.get("separated_constituent_identities_retained") is True
        and row.get("bound_composite_identity_retained") is True
        and row.get("separation_organization_retained") is True
        and not _forbidden.intersection(row)
        for row in _identity_document["rows"]
    )
):
    raise ValueError("PROP-011 source boundary or value-free identity registry is incomplete")


_snapshot_hash_by_path = {
    str(row["snapshot_path"]): str(row["snapshot_hash"])
    for row in _primary["dimer_pages"]
}
_snapshot_hash_by_path[WATER_CLUSTER_PATH] = WATER_CLUSTER_HASH
for _path, _hash in _snapshot_hash_by_path.items():
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-011 target snapshot changed: {_path}")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=_snapshot_hash_by_path[str(row["snapshot_path"])],
    )
    for row in _identity_document["rows"]
)


INTERMOLECULAR_BINDING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-INTERMOLECULAR-BINDING-011",
    title="Exact intermolecular binding by retained state order",
    statement=(
        "An intermolecular binding magnitude is derived only after every named constituent state, the exact "
        "separated-constituent composition, the bound composite state and a finite separation organization remain "
        "held. The higher separated state Takes the strictly lower bound composite state, yielding one exact "
        "positive relation. A record without strict bound order is structural EmptyOne. All 1,299 value-free "
        "identities seal before the complete 1,297-row CCCBDB calculated vector and two reported experimental "
        "water-cluster dissociation rows open; all 96 signed adverse source inscriptions remain explicit and never "
        "become negative SFT numbers."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, separation, composition, magnitude, absence, prediction, record "
        "and extension forms; decide all 256 candidates from admitted exact state order, molecular identity, "
        "intermolecular support, path composition and target-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent exact state-order relation for every finite named constituent tuple, tested against "
        "all 11 official CCCBDB hydrogen-bonded dimers, all 1,297 linked method/basis value rows including every "
        "signed adverse inscription, two reported water-cluster dissociation values with uncertainty, and the "
        "preserved complete 62-page NIST ion-cluster thermochemistry scope record. Calculated, measured, unavailable "
        "and adverse evidence classes remain separate."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two named constituent states compose one exact positive separated endpoint; if one retained composite state "
        "is strictly lower, their ordered Take forces the first exact positive intermolecular binding magnitude."
    ),
    induction_step=(
        "Appending one named positive constituent state to both the separated and bound endpoint compositions "
        "preserves every earlier identity and leaves their exact Take unchanged; equal positive repetition scales "
        "both endpoints and the binding without a new coefficient."
    ),
    exclusions=(
        "no numerical zero; an unbound or unavailable native result is structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no imported intermolecular potential, continuum distance field or force-family equation",
        "no measured or calculated binding target in the law, candidate grammar, forcing or prediction",
        "no fitted interaction coefficient, species correction, basis correction or favorable-row selection",
        "no conflation of calculated CCCBDB rows with reported experimental dissociation values",
        "no deletion of signed adverse, unavailable, unparsed-compendium or source-scope records",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-INTERMOLECULAR-BINDING-011",
    expected_observation_label="exact-positive-separated-Take-bound-or-structural-EmptyOne-with-complete-dimer-cluster-custody",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a retained bound composite below its exact named separated-constituent state does not "
        "yield their exact positive Take; if appending the same constituent state to both endpoints changes the "
        "binding; if a non-bound record requires a negative or numerical-zero SFT value; if any of the 11 dimers, "
        "1,297 linked calculated values, 1,201 positive rows, 96 signed adverse rows, 269 displayed DNF inscriptions, "
        "two reported cluster dissociation values or the complete wider ion-cluster scope record is concealed or "
        "misclassified; if any target opens before sealing; or if a potential, continuum coordinate, fitted "
        "coefficient or species correction enters the executable law."
    ),
)
INTERMOLECULAR_BINDING_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "INDEX_HASH", "INDEX_PATH", "INTERMOLECULAR_BINDING_SPEC",
    "ION_CLUSTER_HASH", "ION_CLUSTER_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_ROOT",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES", "WATER_CLUSTER_HASH", "WATER_CLUSTER_PATH",
)
