"""Source binding for the pre-source-sealed molecular-structure derivation."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.molecular_structure_derivation import MOLECULAR_STRUCTURE_BLUEPRINTS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH = "sft/chemistry/molecular_structure_derivation.py"
DERIVATION_HASH = "sha256:39dab1fec6c9e889b12c65751b46a41b382d8686aaa24569f88d4b98a550c0e5"
PRE_SOURCE_SEAL_PATH = (
    "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_pre_source.json"
)
PRE_SOURCE_PAYLOAD_HASH = "sha256:583e2aa3abd0239e5e7c67d460090e1942958947324e66575b0b6a881f2f7488"
OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_molecular_structure_batch_2.json"
)
DEPENDENCY_AMENDMENT_PATH = (
    "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_dependency_amendment.json"
)
DEPENDENCY_ALIAS_MAP = {
    "SFT-PHYS-KINEMATICS-POSITION-001": "SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001",
    "SFT-PHYS-KINEMATICS-DISPLACEMENT-001": "SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001",
}


SOURCE_RECORDS = {
    "SFT-CHEM-MOL-MOLECULE-001": (
        "molecule-iupac-m04002",
        "IUPAC-GOLD-BOOK-M04002-2026",
        "M04002",
        "sha256:a5058dad716a0233d1a49fb8869d30b581cff6f483317ffdaaf10a3293c52e36",
    ),
    "SFT-CHEM-MOL-GEOMETRY-001": (
        "molecular-geometry-iupac-s06061",
        "IUPAC-GOLD-BOOK-S06061-2026",
        "S06061",
        "sha256:65cc9feaea028f9ab7bd7ed349276522555ebcc66d2f079dc94d55fe9dc7230b",
    ),
    "SFT-CHEM-MOL-ISOMER-001": (
        "isomer-iupac-i03289",
        "IUPAC-GOLD-BOOK-I03289-2026",
        "I03289",
        "sha256:64fa2c9cc58b18b399d22481ee7f37692c7f9c904e4d5fff27c65dd3325393e7",
    ),
    "SFT-CHEM-MOL-INTERMOLECULAR-001": (
        "intermolecular-iupac-i03098",
        "IUPAC-GOLD-BOOK-I03098-2026",
        "I03098",
        "sha256:ba7264c36447a463893ffdfe66e0bce7478e764db59b928911a8f82b59af4b3e",
    ),
    "SFT-CHEM-MOL-SUPRAMOLECULAR-001": (
        "supramolecular-association-iupac-13867",
        "IUPAC-GOLD-BOOK-13867-2026",
        "13867",
        "sha256:34dd0e2a436c762eefbb6ddf8ab84b16b716b252632fc0835ec083d4d4a2551a",
    ),
    "SFT-CHEM-MOL-NETWORK-001": (
        "molecular-network-iupac-n04112",
        "IUPAC-GOLD-BOOK-N04112-2026",
        "N04112",
        "sha256:a146d63f8340f0cf5043e1f9fe2f1cfa8e5fa7c3bf27b8a409e665f40ae2c046",
    ),
}


def validate_pre_source_seal() -> None:
    if hash_file(ROOT / DERIVATION_PATH) != DERIVATION_HASH:
        raise ValueError("target-blind molecular derivation changed after its pre-source seal")
    seal = json.loads((ROOT / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed_hash = seal.pop("sealed_payload_hash", None)
    if claimed_hash != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal) != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("molecular pre-source seal payload is invalid")
    expected = [
        {
            "claim_id": row.claim_id,
            "exact_result": row.exact_result,
            "predicted_observation_label": row.predicted_observation_label,
        }
        for row in MOLECULAR_STRUCTURE_BLUEPRINTS
    ]
    if seal.get("claim_predictions") != expected:
        raise ValueError("molecular predictions differ from the pre-source seal")
    if seal.get("external_source_identities_selected") is not False:
        raise ValueError("molecular derivation was not sealed before source selection")
    if seal.get("external_target_content_opened") is not False:
        raise ValueError("molecular target content was not withheld at derivation seal")
    amendment = json.loads((ROOT / DEPENDENCY_AMENDMENT_PATH).read_text(encoding="utf-8"))
    if amendment.get("schema") != "sft-v3-sealed-derivation-engineering-amendment/1":
        raise ValueError("molecular dependency amendment schema is invalid")
    if amendment.get("original_sealed_payload_hash") != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("molecular dependency amendment is not bound to the original seal")
    if amendment.get("alias_resolution") != DEPENDENCY_ALIAS_MAP:
        raise ValueError("molecular dependency amendment differs from executable alias resolution")
    unchanged_fields = (
        "candidate_dimensions_changed",
        "candidate_census_changed",
        "survivors_changed",
        "exact_results_changed",
        "predicted_observation_labels_changed",
        "external_targets_changed",
    )
    if any(amendment.get(field) is not False for field in unchanged_fields):
        raise ValueError("molecular dependency amendment changes scientific content")


def _target(claim_id: str) -> ChemistryTargetReference:
    target_id, source_id, code, digest = SOURCE_RECORDS[claim_id]
    return ChemistryTargetReference(
        target_id,
        source_id,
        f"https://goldbook.iupac.org/terms/view/{code}/json :: current definition and notes",
        f"experiments/external_sources/chemistry/snapshots/goldbook-terms/{code}.json",
        digest,
    )


def _resolved_dependencies(dependencies: tuple[str, ...]) -> tuple[str, ...]:
    resolved: list[str] = []
    for dependency in dependencies:
        claim_id = DEPENDENCY_ALIAS_MAP.get(dependency, dependency)
        if claim_id not in resolved:
            resolved.append(claim_id)
    return tuple(resolved)


def _bind(blueprint) -> EmpiricalChemistrySpec:
    return EmpiricalChemistrySpec(
        claim_id=blueprint.claim_id,
        title=blueprint.title,
        statement=blueprint.statement,
        dependencies=_resolved_dependencies(blueprint.dependencies),
        generation_rule=blueprint.generation_rule,
        grammar_boundary=blueprint.grammar_boundary,
        dimensions=blueprint.dimensions,
        exact_result=blueprint.exact_result,
        induction_base=blueprint.induction_base,
        induction_step=blueprint.induction_step,
        exclusions=blueprint.exclusions,
        operational_witnesses=blueprint.operational_witnesses,
        experiment_id=blueprint.experiment_id,
        expected_observation_label=blueprint.predicted_observation_label,
        target_rows=(_target(blueprint.claim_id),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition=blueprint.falsification_condition,
    )


validate_pre_source_seal()
MOLECULAR_STRUCTURE_BATCH_2_SPECS = tuple(
    _bind(blueprint) for blueprint in MOLECULAR_STRUCTURE_BLUEPRINTS
)
for _spec in MOLECULAR_STRUCTURE_BATCH_2_SPECS:
    _spec.validate()


__all__ = (
    "MOLECULAR_STRUCTURE_BATCH_2_SPECS",
    "validate_pre_source_seal",
)
