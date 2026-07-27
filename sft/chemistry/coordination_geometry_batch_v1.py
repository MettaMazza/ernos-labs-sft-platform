"""Registered INORG-004 law and complete authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.coordination_geometry_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
CORRECTION_PATH = "experiments/external_sources/chemistry/inorg_004_geometry_identity_correction_v1.json"
CORRECTION_HASH = "sha256:250c45d33906ecc5f02a318e458b30ba34e81f3fc5cae5da04d841d30dc7e4eb"
CORRECTION_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/source-inventory-v1.json"
CORRECTION_INVENTORY_HASH = "sha256:a8fa6ef0e5e25664bf4932fd43097ec4b9e9ee5783dcaafe32e702a9ae82fa73"
IDENTITY_PATH = "experiments/external_sources/chemistry/coordination_geometry_target_identities_v1.json"
IDENTITY_HASH = "sha256:a53997749ddbf807e9371350bcc13a86f419001f16a2511671795839abb792ee"
TARGET_PATH = "experiments/external_sources/chemistry/coordination_geometry_withheld_targets_v1.json"
TARGET_HASH = "sha256:b0ea506c3fa1da5b8a00475d6aedf100084313bdf5fa90b872d727d2dbefda06"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/coordination-geometry-primary-records-v1.json"
PRIMARY_HASH = "sha256:8999d4880febc3f10787de16f3deb80f0016ef91a31050f58664c5cc670a9c18"

SOURCE_FILES = (
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-c01332.json", "sha256:6d775b62304a84679076a7aa8b8eb537b2816c99598b6075b42f510a7142dd72"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/nist-cccbdb-13463393-neutral-geometry.html", "sha256:332816b94435bf9150bd4745f738cac01a6ad78eb404eeb8c57a5ff5da210522"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/nist-cccbdb-13007926-neutral-geometry.html", "sha256:8f3f77d3f79694dd2a1a792c320d7865ca344b020fcf287c14fe6ec257375964"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/nist-cccbdb-13939065-neutral-geometry.html", "sha256:0c53075e7b4d44c9ebcc7cbaf7229bff70be4f14d817aec888e9518c5dc359e6"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/nist-cccbdb-14040110-neutral-geometry.html", "sha256:293ea64c91e16705bb18ee6a767a6b12f8ccac59cf3f79bc752b2cca4aaa5526"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-all-species-identity-list.html", "sha256:7dfb9bb136e369248adf4c127f50ec96e05cffa13a2ec50ca525e46abe4b8a22"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-7646857-neutral-geometry.html", "sha256:881169cd2d6610c46a3e91010b1a1c48398e523ffd470c2fe17e0a24827c834d"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-7784181-neutral-geometry.html", "sha256:2a43c08db1ca3281cb644a110b0338d09f791b8298bf6adc275b551898dd4b10"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-7783633-neutral-geometry.html", "sha256:6c28a00b97c540019a1d48b9d16f068b41741b8dee18ab3a605d5056b055fea1"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-7784363-neutral-geometry.html", "sha256:4e23a3d5488e3aaa1a29cc8c7d789db3c3c2609696f85fde245934cbb558b0a5"),
    ("experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/nist-cccbdb-7783791-neutral-geometry.html", "sha256:ed4ed5bcc451b1dea707db198852e52456de63173e4a79971227b32c3fa25a06"),
)

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (CORRECTION_PATH, CORRECTION_HASH),
    (CORRECTION_INVENTORY_PATH, CORRECTION_INVENTORY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-004 registered authority changed: {path}")

_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identities.get("complete_registered_target_count") != 53
    or _identities.get("target_values_or_payload_hashes_present") is not False
):
    raise ValueError("INORG-004 identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        f"{row['authority']}::{row['source_id']}::{row['source_record_role']}",
        f"{row['source_locator']} :: {row['source_record_role']}",
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identities["rows"]
)

COORDINATION_GEOMETRY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
    title="Exact coordination geometry from complete held orientation and adjacency",
    statement="For one retained central occurrence, coordination geometry is the complete exact signature of every directly attached ligand occurrence, its three-generated-axis held orientation word and every generated boundary adjacency. Coordination count is retained but cannot alone select geometry; the forced space rank is three, the forced boundary rank is two, and adjoining the next direct ligand preserves the complete prior geometry while adding only its own position and adjacency relations.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, incidence, orientation, adjacency, identity, rank, observation and extension forms; decide all 256 forms solely from admitted retained-occurrence, exact incidence, generator-three, boundary-rank-two, graph, information-retention and measured-value-boundary laws.",
    grammar_boundary="Every positive finite complete coordination entity with one retained centre, every directly attached ligand occurrence, one exact three-axis Fold orientation word per ligand, every generated boundary adjacency, all fifty-three value-free registered authority surfaces, all four preserved adverse identity rows and all reported or absent NIST coordinate surfaces.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One retained centre and one direct ligand position force a positive one-position geometry in the three-axis Fold support; its boundary relation is structural EmptyOne until a distinct boundary adjacency is generated.",
    induction_step="Adjoining the next directly attached ligand preserves the centre, every prior occurrence, orientation and adjacency, increases positive coordination count once, and adds exactly the new position and its generated boundary adjacencies while space rank three and boundary rank two remain invariant.",
    exclusions=(
        "no numerical zero; the glyph 0 in an external coordinate is a source inscription and native absence is structural EmptyOne",
        "no negative irrational imaginary floating signed or continuum proof value",
        "no imported coordination-geometry table, shape name, point group, angle, distance, field model or coordination-count lookup in candidate forcing",
        "no selected favourable source row and no deletion of the four original target-identity mismatches or any absent coordinate/reference surface",
        "no source outcome, corrected target value, fitted orientation or target-derived condition in the Fold law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
    expected_observation_label="complete-held-orientation-adjacency-coordination-geometry-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if any direct ligand occurrence, orientation word or generated adjacency is omitted or collapsed; if coordination count alone selects geometry; if rank differs from forced three-space/two-boundary support; if a successor rewrites prior geometry; if any of fifty-three source surfaces, four adverse target-identity mismatches, five positive incidence counts, point-group inscriptions, reported coordinate rows, absent coordinate/reference rows or tampered control is omitted or mismapped; or if an imported table, continuum proof scalar, numerical zero, fitted shape or target-derived correction enters the forcing law.",
)
COORDINATION_GEOMETRY_SPEC.validate()


__all__ = (
    "COORDINATION_GEOMETRY_SPEC",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "SOURCE_FILES",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
