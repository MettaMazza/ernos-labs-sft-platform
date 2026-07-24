"""Post-seal authority bindings for stereochemistry, organic and polymer structure."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.stereochemistry_organic_polymer_derivation import (
    STEREOCHEMISTRY_ORGANIC_POLYMER_BLUEPRINTS,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH = "sft/chemistry/stereochemistry_organic_polymer_derivation.py"
DERIVATION_HASH = "sha256:2a45849856b248dee0eef97a3f99ffb64414475f881b980c231d887ce0970e26"
PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/chemistry_stereochemistry_organic_polymer_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH = "sha256:20dcf6b67d382b7ea55694356c769f7ceb0f8800932d70fab95a0de90b68696e"
OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations_stereochemistry_organic_polymer_batch_1.json"

SOURCE_RECORDS = {
    "SFT-CHEM-STEREO-CHIRALITY-001": (
        "chirality-iupac-composite", "IUPAC-GOLD-BOOK-CHIRALITY-COMPOSITE-2026", "C01058",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/C01058.json",
        "sha256:a787109fa5a2c606b0628013669773016b0245479ed6387584ba027d43e5f01b",
    ),
    "SFT-CHEM-STEREO-ENANTIOMER-001": (
        "enantiomer-iupac-composite", "IUPAC-GOLD-BOOK-ENANTIOMER-COMPOSITE-2026", "E02069",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/E02069.json",
        "sha256:833912292d5eba7d3528d2a31a748a95f4cd4d28b92e896f6e1b5d9ef914935d",
    ),
    "SFT-CHEM-STEREO-DIASTEREOMER-001": (
        "diastereomer-iupac-composite", "IUPAC-GOLD-BOOK-DIASTEREOMER-COMPOSITE-2026", "D01679",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/D01679.json",
        "sha256:4fa09c83930088c3eeea3fd428d370918e6bf98c361673287c0fc8ef9d394078",
    ),
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001": (
        "functional-group-iupac-composite", "IUPAC-GOLD-BOOK-FUNCTIONAL-GROUP-COMPOSITE-2026", "F02555",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/F02555.json",
        "sha256:1fc0f254f488921a762c25454615ea9ec4f40d54736be524fa9f4ff8d79869d1",
    ),
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001": (
        "organic-reaction-family-iupac-composite", "IUPAC-GOLD-BOOK-ORGANIC-REACTION-FAMILY-COMPOSITE-2026", "R05164",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/R05164.json",
        "sha256:e7253285c30faeb217a73b62d4ca4cea7636a626c1306e2eebe8b71960abf6eb",
    ),
    "SFT-CHEM-POLYMER-CHAIN-001": (
        "polymer-chain-iupac-composite", "IUPAC-GOLD-BOOK-POLYMER-CHAIN-COMPOSITE-2026", "M03667",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/M03667.json",
        "sha256:b38c6c106e35763169204b065edaabf18df22bf97f4ea9094db3b8b72383e85a",
    ),
    "SFT-CHEM-POLYMER-DISTRIBUTION-001": (
        "polymer-distribution-iupac-composite", "IUPAC-GOLD-BOOK-POLYMER-DISTRIBUTION-COMPOSITE-2026", "12215",
        "experiments/external_sources/chemistry/snapshots/goldbook-terms/12215.json",
        "sha256:98c415c9e851b41083ffc7ee3b9e1ba2d2b9e81bc6e05bb0dce170dd9733e91a",
    ),
    "SFT-CHEM-BIOMOLECULAR-BOUNDARY-001": (
        "biomolecular-boundary-authority-composite", "EMBL-EBI-CHEBI-BIOMOLECULAR-BOUNDARY-2026", "EBI-CHEBI-STRUCTURE-ROLE",
        "experiments/external_sources/chemistry/snapshots/ebi-chebi-structure-role-extract.html",
        "sha256:d862deab28de555e80751d9fce3fecf4ac4de970d17d9a4c1481dc6976731f24",
    ),
}


def validate_pre_source_seal() -> None:
    if hash_file(ROOT / DERIVATION_PATH) != DERIVATION_HASH:
        raise ValueError("stereochemistry/organic/polymer derivation changed after seal")
    seal = json.loads((ROOT / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal) != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("stereochemistry/organic/polymer seal invalid")
    expected = [
        {
            "claim_id": row.claim_id,
            "exact_result": row.exact_result,
            "predicted_observation_label": row.predicted_observation_label,
        }
        for row in STEREOCHEMISTRY_ORGANIC_POLYMER_BLUEPRINTS
    ]
    if (
        seal.get("claim_predictions") != expected
        or seal.get("external_source_identities_selected") is not False
        or seal.get("external_target_content_opened") is not False
    ):
        raise ValueError("stereochemistry/organic/polymer pre-source boundary invalid")


def _bind(blueprint) -> EmpiricalChemistrySpec:
    target_id, source_id, anchor, path, digest = SOURCE_RECORDS[blueprint.claim_id]
    return EmpiricalChemistrySpec(
        claim_id=blueprint.claim_id,
        title=blueprint.title,
        statement=blueprint.statement,
        dependencies=blueprint.dependencies,
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
        target_rows=(ChemistryTargetReference(target_id, source_id, f"authority source set anchored at {anchor}", path, digest),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition=blueprint.falsification_condition,
    )


validate_pre_source_seal()
STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS = tuple(
    _bind(row) for row in STEREOCHEMISTRY_ORGANIC_POLYMER_BLUEPRINTS
)
for _spec in STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS:
    _spec.validate()

__all__ = ("STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS", "validate_pre_source_seal")
