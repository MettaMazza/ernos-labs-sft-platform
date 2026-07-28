"""Registered ORG-004 law and sealed complete authority surfaces."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.antiaromatic_nonaromatic_distinction_law_v1 import (
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
FAMILY_BOUNDARY_HASH = "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"
LAW_PATH = "sft/chemistry/antiaromatic_nonaromatic_distinction_law_v1.py"
LAW_HASH = "sha256:a9e459b00590a73ff4346cf6ccad670a081e98427e77b68bf691b9c3ddf89d3b"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_004_antiaromatic_nonaromatic_pre_source.json"
PRE_SOURCE_FILE_HASH = "sha256:ec19a1a56f5ffe3dd2759f4d82fb845b1ee111cc72dda9d04e0d582507bbe768"
PRE_SOURCE_PAYLOAD_HASH = "sha256:df89cfe1ebaf37dc299b1679799730bc40ecbf0d0ef4d27d842687b7163a0aa9"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_004_target_identities_v1.json"
IDENTITY_HASH = "sha256:fcc870b511bcd2da94f26b6a9c8eed77ad9c05be3fce6a15869d4c1d6e0c437d"
TARGET_PATH = "experiments/external_sources/chemistry/org_004_withheld_targets_v1.json"
TARGET_HASH = "sha256:e1a73627e34eef30df6159624edf648aeee8458c9c444cc0c764cdff17a754e7"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-004-primary-records-v1.json"
PRIMARY_HASH = "sha256:d46c6ab85ff4fbd9f3813bc292f5b56d8da68b5e68bd2ae0a636d1a22556c780"


for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"ORG-004 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed_prediction_hash = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed_prediction_hash != PRE_SOURCE_PAYLOAD_HASH
    or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("blind_target_content_opened_before_law_and_prediction_seal") is not False
    or _prediction.get("outcome_unopened_blind_target_count") != 2
):
    raise ValueError("ORG-004 pre-source prediction seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 5
    or _identity_document.get("development_observed_target_count") != 3
    or _identity_document.get("outcome_unopened_blind_target_count") != 2
    or _identity_document.get(
        "target_definitions_returned_names_geometry_symmetry_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
    ) is not False
    or len(_identity_rows) != 5
):
    raise ValueError("ORG-004 value-free identity boundary changed")

_target_document = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_target_rows = tuple(_target_document.get("rows", ()))
if len(_target_rows) != 5:
    raise ValueError("ORG-004 complete target vector changed")

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

ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ANTIAROMATIC-NONAROMATIC-DISTINCTION-004",
    title="Exact aromatic, antiaromatic and nonaromatic distinction law",
    statement=(
        "For one retained molecular cycle, the generated Fold recurrence has exactly three structural "
        "classes: complete planar closure, a planar complete support with frustrated return, or a "
        "structurally broken plane/conjugation with EmptyOne recurrence. Their primitive supports are "
        "six, four and EmptyOne respectively; the complete classes append all four ordered pair cells "
        "at each successor, and two positive distinction transfers force the closed, broken, frustrated "
        "stability order without an imported electron-count or measured-energy rule."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, class census, geometry, support, recurrence boundary, "
        "stability order, observation custody and extension alternatives; decide all 256 forms solely "
        "from the admitted Fold assembly, exact arithmetic, graph, order, dynamics, multicentre support, "
        "state-energy, conjugation and aromatic-recurrence dependencies."
    ),
    grammar_boundary=(
        "Every positive finite complete molecular cycle on one retained carrier; both held geometry "
        "states; both held conjugation states; complete two-fibre closure, complete four-cell frustrated "
        "return and structural EmptyOne after an explicit break; all three same-cycle classes; every "
        "positive complete four-cell successor; and the complete five-target authority surface."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "The complete closed base retains two fibres plus four pair cells for support six; the complete "
        "frustrated base retains four pair cells; a structural plane or conjugation break has EmptyOne "
        "recurrence, never numerical zero."
    ),
    induction_step=(
        "Append all four ordered Fold pair cells exactly once to each complete recurrence. Closed support "
        "advances six to ten and frustrated support advances four to eight while every earlier cell, "
        "centre, incidence and class boundary remains held; structural break remains EmptyOne."
    ),
    exclusions=(
        "no numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free or imported native parameter",
        "no Hückel 4n+2 or 4n premise electron-count lookup molecular-name selector or measured energy in survivor selection",
        "no omission of the aromatic antiaromatic or nonaromatic same-cycle alternative",
        "no relabelling a broken plane or conjugation as complete frustrated recurrence",
        "three inspected records remain development-observed correspondence and are not called blind",
        "two NIST CCCBDB outcomes remain inaccessible until after the law and value-free prediction seal",
        "external signed decimal zero and absent inscriptions remain downstream records and never native proof arithmetic",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ANTIAROMATIC-NONAROMATIC-DISTINCTION-004",
    expected_observation_label="complete-aromatic-antiaromatic-nonaromatic-comparative-structure-and-energy-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the same molecular carrier or cycle is changed; if any of the three classes "
        "is omitted; if complete closure, complete frustration or structural EmptyOne is relabelled; if "
        "the primitive supports differ from six, four and EmptyOne or the successors from ten, eight and "
        "EmptyOne; if the two positive order steps disappear; if an electron-count, named species or "
        "measured value selects the law; if any of five source surfaces or any scientific row is omitted; "
        "if either blind outcome was opened before sealing; if the returned structural and energy vector "
        "does not preserve planar distorted antiaromatic, nonplanar bond-alternating nonaromatic and the "
        "positive aromatic/nonaromatic repeated-unit energy separation; or if the absent cyclobutadiene "
        "formation-enthalpy row or any signed/zero external inscription is erased or fabricated."
    ),
)
ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC.validate()


__all__ = (
    "ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC",
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
