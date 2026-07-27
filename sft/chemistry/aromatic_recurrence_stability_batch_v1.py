"""Registered ORG-003 law and sealed complete authority surfaces."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.aromatic_recurrence_stability_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:00ed97e8dec313d65d2b9f6af595e3e3787a99aa60b86814f1a00f318abf011e"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:8b35e1f37dbf80713c47404d946a320da8d7011deaa5dbee7fe8393b58793cee"
BLIND_IDENTITY_PATH = "experiments/external_sources/chemistry/org_003_blind_cccbdb_source_identity_addendum_v1.json"
BLIND_IDENTITY_HASH = "sha256:3a9fa45288af2a49cab7a1ad297d1e673640dfb31e27c8734658d5f12e98d5b0"
BLIND_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-003-blind-cccbdb-v1/source-inventory-v1.json"
BLIND_INVENTORY_HASH = "sha256:75d18e740c853cbaa6d28445bd49b127f023b2f836c1e8afc75a426899542ab7"
LAW_PATH = "sft/chemistry/aromatic_recurrence_stability_law_v1.py"
LAW_HASH = "sha256:a337810c12a1b64e511995f248f05f6f8a3bbd3db7db264f208348738a4f8eae"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_003_aromatic_recurrence_stability_pre_source.json"
PRE_SOURCE_FILE_HASH = "sha256:f8d7938126d337d60fd3c2a2e56889552c74c88b7daf136772b7c94a7ed26085"
PRE_SOURCE_PAYLOAD_HASH = "sha256:eb06a1bd1cf7b4555eb08dc6c7c81dd27c5795fe035a24a53d5b282a4fef9038"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_003_target_identities_v1.json"
IDENTITY_HASH = "sha256:c4ad884ce29b88a63362ac2c32aac3f267f1b3c66626460f5572f851c7057cf7"
TARGET_PATH = "experiments/external_sources/chemistry/org_003_withheld_targets_v1.json"
TARGET_HASH = "sha256:a7e5c32c9686846f9c3cfd643f7b6c62c583b578053fbff004185d8ce7f475aa"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-003-primary-records-v1.json"
PRIMARY_HASH = "sha256:b2efa7fc82cce53960f70088ce43a97794ea4a10c8cfcb75c0563cd72a3fa50d"


for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (BLIND_IDENTITY_PATH, BLIND_IDENTITY_HASH),
    (BLIND_INVENTORY_PATH, BLIND_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"ORG-003 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed_prediction_hash = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed_prediction_hash != PRE_SOURCE_PAYLOAD_HASH
    or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("blind_target_content_fetched_or_opened") is not False
    or _prediction.get("outcome_unopened_blind_target_count") != 3
):
    raise ValueError("ORG-003 pre-source prediction seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 9
    or _identity_document.get("development_observed_target_count") != 6
    or _identity_document.get("outcome_unopened_blind_target_count") != 3
    or _identity_document.get(
        "target_definitions_notes_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 9
):
    raise ValueError("ORG-003 value-free identity boundary changed")
_target_document = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_target_rows = tuple(_target_document.get("rows", ()))
if len(_target_rows) != 9:
    raise ValueError("ORG-003 complete target vector changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        identity["target_id"],
        "::".join(
            (
                identity["authority"],
                identity["source_id"],
                identity["source_record_role"],
                identity["custody_class"],
            )
        ),
        identity["registered_identity"],
        target["opened_snapshot_path"],
        target["opened_snapshot_sha256"],
    )
    for identity, target in zip(_identity_rows, _target_rows)
)

AROMATIC_RECURRENCE_STABILITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003",
    title="Exact aromatic recurrence, support sequence and positive stability law",
    statement=(
        "An aromatic Fold carrier is one complete generated molecular cycle retaining both Fold "
        "boundary fibres and at least one complete layer of their four ordered pair cells. The "
        "primitive support count is six; every lawful successor adds the same four-cell layer, "
        "forcing ten, fourteen and every later positive successor. Opening the complete recurrence "
        "requires one retained positive transfer, so the closed recurrence precedes its opened "
        "localized reference without an imported electron-count or measured-energy rule."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, cycle, Fold boundary, pair-cell layer, return "
        "trace, stability order, observation custody and extension alternatives; decide all 256 "
        "forms solely from admitted Fold assembly, exact graph, finite dynamics, generator three, "
        "multicentre support, energy order, formation-energy accounting, conjugation and "
        "representation-equivalence dependencies."
    ),
    grammar_boundary=(
        "Every positive finite complete molecular cycle; both Fold boundary fibres; every positive "
        "number of complete four-ordered-pair-cell layers; explicit first-return traces; and the "
        "complete nine-target authority surface containing six development-observed correspondence "
        "records and three separately outcome-unopened blind NIST CCCBDB experimental-data pages."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Both Fold boundary fibres plus the first complete four-ordered-pair-cell layer force exact "
        "positive support six on one complete cycle, with structural EmptyOne missing-cell boundary."
    ),
    induction_step=(
        "Append all four ordered Fold pair cells exactly once. Every earlier boundary, layer, centre, "
        "incidence and return record is retained; support increases from six to ten to fourteen and "
        "by the same exact four-cell successor at every positive finite depth."
    ),
    exclusions=(
        "no numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free or imported native parameter",
        "no Hückel 4n+2 rule electron count molecular name or measured energy used to select the survivor",
        "no selected ordered-pair-cell subset or omitted cycle incidence",
        "the six inspected family records are development-observed correspondence and cannot be called blind",
        "the three independent CCCBDB outcomes remain inaccessible until after the value-free law and target seals",
        "external signed enthalpy strings remain downstream held inscriptions and never become native signed arithmetic",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-AROMATIC-RECURRENCE-STABILITY-003",
    expected_observation_label="complete-aromatic-recurrence-structure-and-blind-energy-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the carrier or cycle is incomplete; if either Fold boundary fibre or any "
        "ordered pair cell is missing; if the primitive/successor support counts differ from six, ten "
        "and fourteen; if recurrence lacks an explicit first return; if opening it requires no positive "
        "transfer; if a measured value or imported electron-count rule selects the law; if any of nine "
        "records or any complete scientific table row is omitted; if the blind three-source vector was "
        "opened before sealing; if its exact localized threefold transfer does not exceed the cyclic "
        "transfer by a positive amount clearing the conservative uncertainty envelope; or if signed and "
        "absent external inscriptions are erased or treated as native numbers."
    ),
)
AROMATIC_RECURRENCE_STABILITY_SPEC.validate()


__all__ = (
    "AROMATIC_RECURRENCE_STABILITY_SPEC",
    "BLIND_IDENTITY_PATH",
    "BLIND_INVENTORY_PATH",
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRE_SOURCE_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
