"""Registered INORG-015 law and sealed authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.solid_state_local_coordination_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:87998e9fa168d82dd80c28abc9910502bfb23da0c26cb6b1ecedfb88142642bc"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
LAW_PATH = "sft/chemistry/solid_state_local_coordination_law_v1.py"
LAW_HASH = "sha256:1ee8b5093a3de3b75513173181b73960498069174f5170f9c32217c36f8642f7"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorg_015_target_identities_v1.json"
IDENTITY_HASH = "sha256:a8888f42fb182bf845784b442c5eaa07c4a4899f2ce3d53ae363b5a977dbfdf6"
TARGET_PATH = "experiments/external_sources/chemistry/inorg_015_withheld_targets_v1.json"
TARGET_HASH = "sha256:db016fbc60b05d6da7db32c1f12a6b7d1a903ce6bb8ceef71a3fd5e2c550ac49"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-015-primary-records-v1.json"
PRIMARY_HASH = "sha256:b80128c6cb2e5fbe0c566dd8b77f4cbee8fde5d8e8941e104347c0ba60065dc8"

for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"INORG-015 authority changed: {path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 10
    or _identity_document.get(
        "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 10
):
    raise ValueError("INORG-015 identity boundary changed")

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

SOLID_STATE_LOCAL_COORDINATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015",
    title="Exact solid-state formula, local coordination and ownership law",
    statement=(
        "Chemistry retains one finite complete local solid motif: every species occurrence, "
        "its primitive positive formula ratio, every local bond adjacency, generated repeat "
        "rank one through three, and positive second-constituent support or structural "
        "EmptyOne. Bulk material response is transferred explicitly to Materials."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, composition, formula, bonds, network, "
        "constituent, ownership and extension alternatives; decide all 256 forms from the "
        "admitted exact-arithmetic, graph, generator-three, stoichiometry, bond, coordination "
        "and cluster dependencies."
    ),
    grammar_boundary=(
        "Every positive finite complete local occurrence motif with exact local adjacency, "
        "primitive positive formula, generated repeat rank one, two or three, and explicit "
        "Chemistry-to-Materials handoff; all ten frozen coordination-network and returned "
        "mixed-crystal surfaces."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One positive complete local motif has a complete occurrence multiset, a uniquely "
        "gcd-reduced positive formula, explicit local bonds and at least one generated repeat axis."
    ),
    induction_step=(
        "Appending one fresh species occurrence and one retained local bond preserves every prior "
        "occurrence and adjacency and recomputes the unique primitive positive formula without "
        "adding a catalogue rule."
    ),
    exclusions=(
        "no numerical zero; absent second-constituent support is structural EmptyOne",
        "no negative irrational imaginary signed continuum fitted free or imported parameter",
        "no nominal formula substituted for the complete occurrence multiset",
        "no infinite or continuum lattice imported into the local Chemistry law",
        "no bulk material response claimed by Chemistry",
        "no coordination-network definition or mixed-crystal outcome used to select the law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-SOLID-STATE-LOCAL-COORDINATION-015",
    expected_observation_label="complete-local-solid-and-ownership-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any local occurrence or bond is omitted, if the formula is not the "
        "primitive positive count ratio, if repeat rank exceeds generator three, if absence uses "
        "numerical zero, if Chemistry claims bulk response, if the returned mixed-crystal identity "
        "mismatch is hidden, if any of ten source surfaces is removed, or if outcomes open before "
        "prediction sealing."
    ),
)
SOLID_STATE_LOCAL_COORDINATION_SPEC.validate()

__all__ = (
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "SOLID_STATE_LOCAL_COORDINATION_SPEC",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
