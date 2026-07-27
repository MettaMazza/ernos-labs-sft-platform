"""Registered ORG-001 law and sealed complete authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.conjugated_support_law_v1 import (
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
LAW_PATH = "sft/chemistry/conjugated_support_law_v1.py"
LAW_HASH = "sha256:69590fd71a11af17729aeda74eabb6340678be8e8f401754f5ee2d958d4d3833"
SPECTRAL_IDENTITY_PATH = "experiments/external_sources/chemistry/org_001_spectral_source_identity_addendum_v1.json"
SPECTRAL_IDENTITY_HASH = "sha256:d4839729d56d75088a5f0c09c3bb8e37070f183ebe8899e6ae579a7b659332c8"
SPECTRAL_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-spectral-addendum-v1/source-inventory-v1.json"
SPECTRAL_INVENTORY_HASH = "sha256:9148de7fe76de89018bee28c60e82ad3f560df97ca7b5e22a5cc6790b11925fe"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_001_conjugated_support_pre_source.json"
PRE_SOURCE_FILE_HASH = "sha256:cd58687ee685dff26578b5e36a31e13579565d22a5c589939fb592a01c830257"
PRE_SOURCE_PAYLOAD_HASH = "sha256:0d5b02fc0add6291a0ca99f3564ffbd10e058735740f0b609bd229b45ccb778a"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_001_target_identities_v1.json"
IDENTITY_HASH = "sha256:8d63eeae30f819ec961ac73e98add98258ad48faa670d0ea140ed9bd2271a893"
V1_TARGET_PATH = "experiments/external_sources/chemistry/org_001_withheld_targets_v1.json"
V1_TARGET_HASH = "sha256:adade1c9a6bed06b83a745680a63f73f0685cbf422bb4a2f3f5f0bf9830e0e7f"
V1_PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-001-primary-records-v1.json"
V1_PRIMARY_HASH = "sha256:bef1acc4528270b903349dfb49d87dd12548bd81cca90ffab1f15865821f5d28"
TARGET_PATH = "experiments/external_sources/chemistry/org_001_withheld_targets_v2.json"
TARGET_HASH = "sha256:580934f71639b83e6e1f5e24ddd87e8bb19db150a6bdae3c4b6e899a34b74192"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-001-primary-records-v2.json"
PRIMARY_HASH = "sha256:6d40642ebbd21ff6b9abb72a09e0cc0b76a40539540b50d07add3666a5375550"


for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (SPECTRAL_IDENTITY_PATH, SPECTRAL_IDENTITY_HASH),
    (SPECTRAL_INVENTORY_PATH, SPECTRAL_INVENTORY_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (V1_TARGET_PATH, V1_TARGET_HASH),
    (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"ORG-001 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed_prediction_hash = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed_prediction_hash != PRE_SOURCE_PAYLOAD_HASH
    or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("external_target_content_opened_after_target_identity_seal") is not False
):
    raise ValueError("ORG-001 pre-source prediction seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 10
    or _identity_document.get(
        "target_definitions_coordinates_peaks_intensities_values_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 10
):
    raise ValueError("ORG-001 value-free identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        "::".join(
            (
                row["authority"],
                row["source_id"],
                row["source_record_role"],
                row["custody_class"],
            )
        ),
        row["registered_identity"],
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identity_rows
)

CONJUGATED_SUPPORT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CONJUGATED-SUPPORT-001",
    title="Exact connected alternating conjugated-support law",
    statement=(
        "A conjugated Fold support is one finite connected molecular subcarrier in which every "
        "adjacent incidence retains one of the two forced Fold fibres, every successive incidence "
        "carries the opposed fibre through a shared atom occurrence, and every atom and incidence "
        "is retained. A fresh occurrence has one unique opposed-fibre successor."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, connectivity, fibres, alternation, coverage, "
        "propagation, observation and extension alternatives; decide all 256 forms from admitted "
        "form enforcement, exact graph, distinction, conservation, molecular, bond-order and "
        "organic-carrier dependencies."
    ),
    grammar_boundary=(
        "Every finite complete molecular path of at least three distinct atom occurrences and its "
        "complete adjacent incidence support; all ten frozen terminology, experimental structure, "
        "separated-support control, vibrational and UV-visible surfaces."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Three distinct atom occurrences joined by the two opposed Fold support fibres supply the "
        "first complete connected alternating path."
    ),
    induction_step=(
        "Appending one fresh atom occurrence preserves every prior incidence and uniquely appends "
        "the fibre opposed to the formerly terminal incidence; repetition, omission or duplicated "
        "identity halts."
    ),
    exclusions=(
        "no numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary signed continuum fitted free or imported parameter",
        "no conventional single/double-bond notation used to select the two Fold fibres",
        "no resonance notation or electron-count rule imported into forcing",
        "no selected favourable subpath or omitted incidence",
        "no definition, molecular name, coordinate, vibration or spectrum opened to select the law",
        "the preserved V1 parser overrun cannot be hidden or treated as evidence",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CONJUGATED-SUPPORT-001",
    expected_observation_label="complete-connected-alternating-conjugated-support-structure-and-spectrum-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if its path is disconnected; if any atom, incidence or support fibre is "
        "omitted; if adjacent fibres repeat; if an external name, definition, coordinate or "
        "spectrum selects the survivor; if the separated-double-bond control is misclassified from "
        "bond counts alone; if any of ten rows or any of 502 UV-visible points is lost; if the "
        "external signed control inscription is erased or made native; if the V1 parser overrun is "
        "hidden; or if outcomes open before the value-free prediction seal."
    ),
)
CONJUGATED_SUPPORT_SPEC.validate()


__all__ = (
    "CONJUGATED_SUPPORT_SPEC",
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRE_SOURCE_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "SPECTRAL_IDENTITY_PATH",
    "SPECTRAL_INVENTORY_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
    "V1_PRIMARY_PATH",
    "V1_TARGET_PATH",
)
