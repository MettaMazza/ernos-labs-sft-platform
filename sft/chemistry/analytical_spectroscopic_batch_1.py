"""Post-seal authority bindings for analytical and spectroscopic structure."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.analytical_spectroscopic_derivation import ANALYTICAL_SPECTROSCOPIC_BLUEPRINTS
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH = "sft/chemistry/analytical_spectroscopic_derivation.py"
DERIVATION_HASH = "sha256:eeddce8a3e937d7e78fdad233e52e37e17401d2151136abf8cac19331030fa08"
PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/chemistry_analytical_spectroscopic_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH = "sha256:7a94f1bf8630a5c0908022749f8f9b791c5ec0bb39e261105eb3f896f1f7708b"
OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations_analytical_spectroscopic_batch_1.json"

SOURCE_RECORDS = {
    "SFT-CHEM-ANALYTICAL-SAMPLE-001": ("analytical-sample-iupac-composite", "IUPAC-GOLD-BOOK-ANALYTICAL-SAMPLE-COMPOSITE-2026", "S05451", "experiments/external_sources/chemistry/snapshots/goldbook-terms/S05451.json", "sha256:f2d630c6a9a8ec0ab1304a6e9e3acf1bc495b9b3f2d5f3958375aa0c3fafa184"),
    "SFT-CHEM-ANALYTICAL-CALIBRATION-001": ("analytical-calibration-iupac-composite", "IUPAC-GOLD-BOOK-ANALYTICAL-CALIBRATION-COMPOSITE-2026", "C00775", "experiments/external_sources/chemistry/snapshots/goldbook-terms/C00775.json", "sha256:9a50ffb4e909ae78ac6ccf2cfa69db372a7ff659db4fb88b48e89e79322b69c0"),
    "SFT-CHEM-ANALYTICAL-SELECTIVITY-001": ("analytical-selectivity-iupac-composite", "IUPAC-GOLD-BOOK-ANALYTICAL-SELECTIVITY-COMPOSITE-2026", "S05564", "experiments/external_sources/chemistry/snapshots/goldbook-terms/S05564.json", "sha256:24cfb5654b5ba14eb99cc4dfe0c01efa7a251be91937a33000f362ba8a9730f6"),
    "SFT-CHEM-SPEC-MASS-001": ("mass-spectroscopy-iupac-composite", "IUPAC-GOLD-BOOK-MASS-SPECTROSCOPY-COMPOSITE-2026", "M03749", "experiments/external_sources/chemistry/snapshots/goldbook-terms/M03749.json", "sha256:bb7b4631fab65d61fd3c0f8b6257ae91bc87da91ceea23a961f4c824f20b4e56"),
    "SFT-CHEM-SPEC-INFRARED-001": ("infrared-spectroscopy-iupac-composite", "IUPAC-GOLD-BOOK-INFRARED-SPECTROSCOPY-COMPOSITE-2026", "08618", "experiments/external_sources/chemistry/snapshots/goldbook-terms/08618.json", "sha256:0be3cc15940bfcf345e61af54ef378022de8f2c32b7e566b7d4ed25f69c553ab"),
    "SFT-CHEM-SPEC-UVVIS-001": ("uv-visible-spectroscopy-iupac-composite", "IUPAC-GOLD-BOOK-UVVISIBLE-SPECTROSCOPY-COMPOSITE-2026", "S05696", "experiments/external_sources/chemistry/snapshots/goldbook-terms/S05696.json", "sha256:bcf4022ed1743c6445d1c6a2dc88d616adad7f833c299734f1b3fc3b45652a7d"),
    "SFT-CHEM-SPEC-ROT-VIB-001": ("rotation-vibration-iupac-composite", "IUPAC-GOLD-BOOK-ROTATION-VIBRATION-COMPOSITE-2026", "08676", "experiments/external_sources/chemistry/snapshots/goldbook-terms/08676.json", "sha256:fa1bdd34ab2e93cce09dd22311bba6d9c1e3ee4221a285510eca2b7ce8e3e647"),
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001": ("complete-analytical-record-authority-composite", "IUPAC-NIST-COMPLETE-ANALYTICAL-RECORD-COMPOSITE-2026", "M03796", "experiments/external_sources/chemistry/snapshots/goldbook-terms/M03796.json", "sha256:f27104514cc2af6ad31064e74244121a076fc3c795f3f636e4f7f8face60e9a1"),
}


def validate_pre_source_seal() -> None:
    if hash_file(ROOT / DERIVATION_PATH) != DERIVATION_HASH:
        raise ValueError("analytical/spectroscopic derivation changed after seal")
    seal = json.loads((ROOT / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal) != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("analytical/spectroscopic seal invalid")
    expected = [{"claim_id": row.claim_id, "exact_result": row.exact_result, "predicted_observation_label": row.predicted_observation_label} for row in ANALYTICAL_SPECTROSCOPIC_BLUEPRINTS]
    if seal.get("claim_predictions") != expected or seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False:
        raise ValueError("analytical/spectroscopic pre-source boundary invalid")


def _bind(blueprint) -> EmpiricalChemistrySpec:
    target_id, source_id, anchor, path, digest = SOURCE_RECORDS[blueprint.claim_id]
    return EmpiricalChemistrySpec(
        claim_id=blueprint.claim_id, title=blueprint.title, statement=blueprint.statement,
        dependencies=blueprint.dependencies, generation_rule=blueprint.generation_rule,
        grammar_boundary=blueprint.grammar_boundary, dimensions=blueprint.dimensions,
        exact_result=blueprint.exact_result, induction_base=blueprint.induction_base,
        induction_step=blueprint.induction_step, exclusions=blueprint.exclusions,
        operational_witnesses=blueprint.operational_witnesses, experiment_id=blueprint.experiment_id,
        expected_observation_label=blueprint.predicted_observation_label,
        target_rows=(ChemistryTargetReference(target_id, source_id, f"authority source set anchored at {anchor}", path, digest),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition=blueprint.falsification_condition,
    )


validate_pre_source_seal()
ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS = tuple(_bind(row) for row in ANALYTICAL_SPECTROSCOPIC_BLUEPRINTS)
for _spec in ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS:
    _spec.validate()

__all__ = ("ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS", "validate_pre_source_seal")
