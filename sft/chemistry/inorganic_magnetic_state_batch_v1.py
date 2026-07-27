"""Registered INORG-009 law and complete sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.inorganic_magnetic_state_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/inorganic_magnetic_state_law_v1.py"
LAW_HASH = "sha256:27c299058fa6ec1489155395766f280e3cd6e29d0786828d0e75c2d0018e9452"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_009_magnetic_shared_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:2ed4e683e793e9774b0e8b23e4d8c22e8a0f112646896bda78d749235cd26079"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorganic_magnetic_state_target_identities_v1.json"
IDENTITY_HASH = "sha256:0c32836405b1bc88a148e896b2f4cd3634100ae364013ec6441150d9d35943a8"
TARGET_PATH = "experiments/external_sources/chemistry/inorganic_magnetic_state_withheld_targets_v1.json"
TARGET_HASH = "sha256:21eda342124fc2d0884b59d96e28fc16e44d42b97481be10abbe296360b49010"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorganic-magnetic-state-primary-records-v1.json"
PRIMARY_HASH = "sha256:2c244acf074d8b3a9fdffb170f356d270f90aa8b35e5aff4cf8dd35c1f35c7b6"
SHARED_IDENTITY_PATH = "experiments/external_sources/chemistry/magnetic_response_target_identities_v1.json"
SHARED_IDENTITY_HASH = "sha256:aeaf62719a5c7699f9743722df5ffbafb7ffc3337e366f8321bc2a2dbe357259"
SHARED_TARGET_PATH = "experiments/external_sources/chemistry/magnetic_response_withheld_targets_v1.json"
SHARED_TARGET_HASH = "sha256:7ce119e64518c20376cdba0f1a8e0814ee76d48a6ee50acd562cfd4f44c8211d"
SHARED_PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-012-magnetic-response-v1/magnetic-response-primary-records-v1.json"
SHARED_PRIMARY_HASH = "sha256:af4fc413c056cd2caf8867b855f4ed948f2ba62a9576265c571f05dfd5a6d3d2"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH), (ADDENDUM_PATH, ADDENDUM_HASH),
    (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
    (SHARED_IDENTITY_PATH, SHARED_IDENTITY_HASH), (SHARED_TARGET_PATH, SHARED_TARGET_HASH), (SHARED_PRIMARY_PATH, SHARED_PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-009 registered authority changed: {path}")


_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 177
    or _identity_document.get("target_values_orientations_presence_flags_definitions_outcomes_or_payload_hashes_present") is not False
    or len(_rows) != 177
    or tuple(row["source_record_ordinal"] for row in _rows) != tuple(range(1, 178))
):
    raise ValueError("INORG-009 value-free target identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"], f"{row['authority']}::{row['source_id']}::{row['source_record_role']}::{row['custody_class']}",
        f"{row['registered_identity']} :: {row.get('section', row['source_id'])}",
        row.get("snapshot_path", SHARED_TARGET_PATH), row.get("snapshot_sha256", SHARED_TARGET_HASH),
    )
    for row in _rows
)


INORGANIC_MAGNETIC_STATE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-INORGANIC-MAGNETIC-STATE-009",
    title="Exact inorganic unpaired-support magnetic-state law",
    statement="A coordination entity's magnetic state is the complete retained support of every unpaired electron occurrence and its held spin fibre. Complete complementary pairing closes unpaired support to structural EmptyOne, forcing spin width One, a held repelled-from-field relation and the diamagnetic class. Positive unpaired support forces exact moment support equal to its cardinality, spin width one successor beyond it, a held drawn-into-field relation and the paramagnetic class. Appending one unpaired occurrence increments moment support and width exactly once. No signed susceptibility, irrational spin-only square root, fitted g-factor or species lookup enters forcing.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, support, balance, moment, width, direction, classification and extension choices; decide all 256 candidates solely from admitted exact spin, exclusion, occupancy, magnetic-response and INORG-006/007 dependencies.",
    grammar_boundary="Every finite complete unpaired electron occurrence support on one retained coordination entity; structural EmptyOne or positive cardinality; both held field relations; all three frozen IUPAC definitions and all 174 shared sealed NIST magnetic-response cells.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="Complete complementary pairing leaves structural EmptyOne unpaired support, spin width One and the diamagnetic/repelled held class. The first unpaired occurrence is the first positive moment support, spin width two and the paramagnetic/drawn held class.",
    induction_step="Appending one distinct unpaired occurrence preserves every prior occurrence and fibre, increments exact moment support and spin width once, and preserves the paramagnetic/drawn class without a new parameter or exception.",
    exclusions=(
        "no numerical zero; complete paired closure is structural EmptyOne",
        "no negative irrational imaginary floating signed continuum or square-root proof quantity",
        "no imported spin-only moment formula signed magnetic quantum number susceptibility sign rule fitted g-factor or species table",
        "no dimensional magnetic constant or measured moment in generation enumeration or survivor decision",
        "no deletion of 136 exact magnitudes, 38 structural absences, held source orientations or unavailable surfaces",
        "no recapture or relabeling of shared admitted PROP-012 evidence",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-INORGANIC-MAGNETIC-STATE-009",
    expected_observation_label="complete-unpaired-classification-and-177-row-magnetic-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if unpaired support is incomplete or duplicated; if balanced support does not close to structural EmptyOne; if positive moment support or spin width differs from the complete unpaired count and its successor; if the held field/class pair differs; if forbidden arithmetic, a square-root formula, fitted g-factor, signed proof scalar or species lookup enters forcing; if any of 177 rows, 136 exact magnitudes, 38 structural absences or source orientations is removed; or if shared evidence is recaptured or relabeled.",
)
INORGANIC_MAGNETIC_STATE_SPEC.validate()


__all__ = (
    "ADDENDUM_PATH", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH", "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH", "IDENTITY_PATH", "INORGANIC_MAGNETIC_STATE_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "SHARED_IDENTITY_PATH", "SHARED_PRIMARY_PATH", "SHARED_TARGET_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
