"""Registered INORG-001 law and complete IUPAC/NIST coordination structure surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.coordination_entity_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/inorg-001-coordination-entity-v1"
SPEC_PATH = "experiments/external_sources/chemistry/coordination_entity_capture_spec_v1.json"
SPEC_HASH = "sha256:827e03cff335a2e3dd5110bb86620e03b83aef37dd450d5b4bd64b9bda167c10"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:860ac64ca2e6f3febcdcafd64ac1fa79f5c7ac6c4e72fbdd7e884ee6e5255ae7"
IDENTITY_PATH = "experiments/external_sources/chemistry/coordination_entity_target_identities_v1.json"
IDENTITY_HASH = "sha256:8361d4e58069a692c8e101ef827d4d69faa6721348741eb1112767dc4fb94ea0"
TARGET_PATH = "experiments/external_sources/chemistry/coordination_entity_withheld_targets_v1.json"
TARGET_HASH = "sha256:a0458a8f2bb428d408b610fcf558263283b18604147d2423b3620845366bb9c3"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/coordination-entity-primary-records-v1.json"
PRIMARY_HASH = "sha256:378e538a21e9a52e7353c187b3258527b5b050c791ac9c9fe38dd32d80cfbf4a"

SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/iupac-central-atom.json", "sha256:0b54c0a0c7f9e4f4dafbc8ef72b10f983fe84029905b93d0e3abf8d4db89567d"),
    (f"{SNAPSHOT_ROOT}/iupac-coordination-entity.json", "sha256:4019d4af2537787bbcb95ca7d94446b8d03a73751075c1401e1d74babd77145b"),
    (f"{SNAPSHOT_ROOT}/iupac-ligands.json", "sha256:e92c4fe3e4fadefef66f21481b61fdd9bab374bfda4a4ce59149866693f03fac"),
    (f"{SNAPSHOT_ROOT}/nist-cccbdb-ferrocene-experimental-geometry.html", "sha256:b6f9f0c8bdd15df1d166a3b2b9cf7c8517d72529976ff062caaca36d44ad97f0"),
    (f"{SNAPSHOT_ROOT}/nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "sha256:62d6da495b385e07a80ea58d986b40ed11973dd639863055e38e23493222159d"),
)
for path, expected in ((SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-001 registered source changed: {path}")

_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if _identities.get("complete_registered_target_count") != 20 or _identities.get("target_values_or_hashes_present") is not False:
    raise ValueError("INORG-001 value-free identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        f"{row['authority']}-{row['source_record_role']}",
        f"{row['source_locator']} :: {row['source_record_role']}",
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identities["rows"]
)

COORDINATION_ENTITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
    title="Coordination entity and retained central-ligand identity law",
    statement="A coordination entity is the complete retained carrier of one central occurrence, every distinct ligand occurrence and every positive central-ligand incidence. Central and surrounding roles are forced by the common incidence structure; repeated ligand labels never erase occurrence identity. Adding the next complete ligand incidence preserves every prior identity and attachment.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, role, identity, attachment, composition, absence, observation and extension forms. Decide all 256 forms only by admitted Fold identity, finite incidence, exact composition, source-boundary and successor laws.",
    grammar_boundary="Every positive finite single-central coordination support with one or more distinct attached ligand occurrences, tested after seal against all twenty registered IUPAC and NIST definition, structure, value, reference and limitation records.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One central occurrence and one positive attached ligand occurrence force the first complete coordination entity.",
    induction_step="Appending the next distinct ligand occurrence by one positive incidence to the same retained central occurrence preserves every prior entity, central, ligand-group, ligand-occurrence and attachment identity.",
    exclusions=(
        "no numerical zero; glyph 0 is source/interface absence only and structural absence is EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum proof value",
        "no imported coordination-number, valence-bond, ligand-field, molecular-orbital or geometry model",
        "no observed IUPAC definition, NIST formula, point group, link count, coordinate, reference or limitation before prediction seal",
        "no fitted bond length, selected complex, omitted structural row or source-derived correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
    expected_observation_label="complete-coordination-entity-structure-correspondence",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if a coordination entity does not retain its central occurrence, any ligand occurrence or any central-ligand incidence; if repeated ligand labels collapse occurrences; if adding one ligand replaces prior identity; if any of twenty registered authority records changes or is omitted; if NIST Fe(CO)5 or ferrocene lacks the retained Fe-ligand structure; if reported absences or disclaimers are suppressed; or if numerical zero, signed, continuum, fitted or target-derived proof structure enters the law.",
)
COORDINATION_ENTITY_SPEC.validate()

__all__ = (
    "COORDINATION_ENTITY_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "SOURCE_FILES", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
