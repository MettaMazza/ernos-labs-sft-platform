"""Registered INORG-010 law and complete sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.organometallic_metal_carbon_bond_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:87998e9fa168d82dd80c28abc9910502bfb23da0c26cb6b1ecedfb88142642bc"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
LAW_PATH = "sft/chemistry/organometallic_metal_carbon_bond_law_v1.py"
LAW_HASH = "sha256:6a68716528b3e76ce698c9e40d2b4c9b69d7cbb807761e6afb3edf1ca7c01f25"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorg_010_target_identities_v1.json"
IDENTITY_HASH = "sha256:7262a7a2b3940d00812151560d243a6362bbca4edaebac98d3a67c7072c44f1d"
TARGET_PATH = "experiments/external_sources/chemistry/inorg_010_withheld_targets_v1.json"
TARGET_HASH = "sha256:ee172a1f270bfbd5d1731bc0cd625b748f7899264c1e1c81593fb5cccc8095f4"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-010-primary-records-v1.json"
PRIMARY_HASH = "sha256:9dfa92b8c634d7d8e869a25ed4aec67065e59519583d9af3ccd42f3e55ad58ba"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-010 registered authority changed: {path}")


_identity = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_rows = tuple(_identity.get("rows", ()))
if (
    _identity.get("complete_registered_target_count") != 12
    or _identity.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False
    or len(_rows) != 12
    or tuple(row["source_record_ordinal"] for row in _rows) != tuple(range(1, 13))
):
    raise ValueError("INORG-010 value-free target boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"], f"{row['authority']}::{row['source_id']}::{row['source_record_role']}::{row['custody_class']}",
        row["registered_identity"], row["snapshot_path"], row["snapshot_sha256"],
    )
    for row in _rows
)


ORGANOMETALLIC_METAL_CARBON_BOND_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010",
    title="Exact direct metal-carbon organometallic bond law",
    statement="A metal-carbon organometallic bond is one direct generated incidence between a retained admitted centre occurrence and a retained carbon occurrence on one chemical entity, with complete positive held bond-electron support. The exact organometallic bond topology is the complete distinct incidence support and its positive cardinality. Structural absence of direct incidence remains EmptyOne and cannot be promoted by a compound name, proximity, species table or fitted exception.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, centre, carbon, topology, electron, multiplicity, classification and extension choices; decide all 256 candidates solely from admitted chemical-entity, element, bond, composition, electron-support and coordination dependencies.",
    grammar_boundary="Every finite one-entity support of distinct direct admitted-centre/carbon incidences with positive held electron support; structural EmptyOne absence; all twelve frozen IUPAC criterion, scope, example, context and exclusion surfaces.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="Structural EmptyOne contains no direct incidence. The first positive direct centre-carbon incidence forces count one and the organometallic class.",
    induction_step="Appending one fresh direct centre-carbon incidence preserves every previous incidence and held electron occurrence and increments the exact direct-incidence count once without changing the classification rule.",
    exclusions=(
        "no numerical zero; absence of direct incidence is structural EmptyOne",
        "no negative irrational imaginary floating signed continuum fitted free or imported parameter",
        "no conventional metal list species lookup compound-name classification proximity rule or formula-fragment substitution",
        "no observed example, scope statement or exclusion used to select the survivor",
        "no omission of any frozen example, context, absence or source disclaimer surface",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010",
    expected_observation_label="complete-direct-bond-criterion-scope-example-and-exclusion-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if the chemical entity, centre, carbon, direct adjacency or held electron support is lost or duplicated; if structural absence becomes numerical zero or a positive class; if the exact count differs from complete direct incidence support; if a name, conventional list, species lookup, observed example or fitted exception selects the law; if any of twelve IUPAC surfaces is removed or changed; or if prediction accesses outcomes before sealing.",
)
ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.validate()


__all__ = (
    "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH", "FAMILY_REGISTRY_PATH", "IDENTITY_HASH", "IDENTITY_PATH",
    "ORGANOMETALLIC_METAL_CARBON_BOND_SPEC", "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
