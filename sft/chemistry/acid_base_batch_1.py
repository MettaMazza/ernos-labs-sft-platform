"""Post-seal authoritative bindings for the first acid/base batch."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.acid_base_derivation import ACID_BASE_BLUEPRINTS
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH = "sft/chemistry/acid_base_derivation.py"
DERIVATION_HASH = "sha256:50e328d932a018c7895f07d723b31076f96e99529b38504df1490ccaa764008c"
PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/chemistry_acid_base_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH = "sha256:4be0b7e80ca75740fb8cec8a4ca2dfd747a4ac6a0e4c4cb3375a94c0e74bdc01"
OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations_acid_base_batch_1.json"


SOURCE_RECORDS = {
    "SFT-CHEM-AB-ACID-BASE-001": ("conjugate-acid-base-iupac-composite", "IUPAC-GOLD-BOOK-ACID-BASE-COMPOSITE-2026", "C01266", "experiments/external_sources/chemistry/snapshots/goldbook-terms/C01266.json", "sha256:1ac0d6138e316d6230d10b2e7f99d4837175fcb640e824a8cb2249100221a504"),
    "SFT-CHEM-AB-PROTON-TRANSFER-001": ("proton-transfer-iupac-p04915", "IUPAC-GOLD-BOOK-P04915-2026", "P04915", "experiments/external_sources/chemistry/snapshots/goldbook-terms/P04915.json", "sha256:72d9b1431f3daa6b0190094d8400bc73b31e786b7d69b4052632297b4b709d33"),
    "SFT-CHEM-AB-LEWIS-001": ("lewis-acid-base-iupac-composite", "IUPAC-GOLD-BOOK-LEWIS-COMPOSITE-2026", "L03508", "experiments/external_sources/chemistry/snapshots/goldbook-terms/L03508.json", "sha256:9fa013b12d6d0e3f305883a0db53dac7484e292e0288e2c3d0ba9625cfb2011c"),
    "SFT-CHEM-AB-AMPHOTERIC-001": ("amphoteric-iupac-a00306", "IUPAC-GOLD-BOOK-A00306-2026", "A00306", "experiments/external_sources/chemistry/snapshots/goldbook-terms/A00306.json", "sha256:70ab5021338400d9f02cbecc5c45b9f4271792e919d880aafff81684739022ab"),
    "SFT-CHEM-AB-BUFFER-001": ("buffer-iupac-didac-e15", "IUPAC-DIDAC-E15-2026", "IUPAC-DIDAC-E15", "experiments/external_sources/chemistry/snapshots/iupac-didac-buffer-e15-extract.html", "sha256:570a91d1a7de35b22a8469c117f10af9e4bed3012ae61f54362fe45534b3d01e"),
}


def validate_pre_source_seal() -> None:
    if hash_file(ROOT / DERIVATION_PATH) != DERIVATION_HASH:
        raise ValueError("target-blind acid/base derivation changed after its pre-source seal")
    seal = json.loads((ROOT / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed_hash = seal.pop("sealed_payload_hash", None)
    if claimed_hash != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal) != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("acid/base pre-source seal payload is invalid")
    expected = [
        {"claim_id": row.claim_id, "exact_result": row.exact_result, "predicted_observation_label": row.predicted_observation_label}
        for row in ACID_BASE_BLUEPRINTS
    ]
    if seal.get("claim_predictions") != expected:
        raise ValueError("acid/base predictions differ from the pre-source seal")
    if seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False:
        raise ValueError("acid/base derivation was not sealed before source selection")


def _bind(blueprint) -> EmpiricalChemistrySpec:
    target_id, source_id, code, snapshot_path, digest = SOURCE_RECORDS[blueprint.claim_id]
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
        target_rows=(ChemistryTargetReference(target_id, source_id, f"official IUPAC source set anchored at {code}", snapshot_path, digest),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition=blueprint.falsification_condition,
    )


validate_pre_source_seal()
ACID_BASE_BATCH_1_SPECS = tuple(_bind(row) for row in ACID_BASE_BLUEPRINTS)
for _spec in ACID_BASE_BATCH_1_SPECS:
    _spec.validate()


__all__ = ("ACID_BASE_BATCH_1_SPECS", "validate_pre_source_seal")
