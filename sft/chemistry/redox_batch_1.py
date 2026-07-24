"""Post-seal authoritative bindings for affinity, polarity and redox."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.redox_derivation import REDOX_BLUEPRINTS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent.parent
DERIVATION_PATH = "sft/chemistry/redox_derivation.py"
DERIVATION_HASH = "sha256:803baf2ecb15116c290e38d3007e12b553a10db3e16fc5b747fe08f44c730e48"
PRE_SOURCE_SEAL_PATH = "experiments/sealed_predictions/chemistry_redox_batch_1_pre_source.json"
PRE_SOURCE_PAYLOAD_HASH = "sha256:ffbb0219ac03bd18dd37ab0ae9594ad961fbda7dc61491b1c74c3a7a4dffc1a9"
OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations_redox_batch_1.json"

SOURCE_RECORDS = {
    "SFT-CHEM-ELECTRONEGATIVITY-001": ("electronegativity-iupac-composite", "IUPAC-GOLD-BOOK-ELECTRONEGATIVITY-COMPOSITE-2026", "E01990", "experiments/external_sources/chemistry/snapshots/goldbook-terms/E01990.json", "sha256:bc2888f84a2a3efc53f89738797c88528af75cd0564295e2a1d4138cd1c778e3"),
    "SFT-CHEM-BOND-POLARITY-001": ("bond-polarity-iupac-composite", "IUPAC-GOLD-BOOK-BOND-POLARITY-COMPOSITE-2026", "08195", "experiments/external_sources/chemistry/snapshots/goldbook-terms/08195.json", "sha256:a907133200cc3296e7ecdb7c8970ae8ce35af7b6d3b44d6746f7d18ad5086d41"),
    "SFT-CHEM-REDOX-OXIDATION-STATE-001": ("oxidation-state-iupac-o04365", "IUPAC-GOLD-BOOK-O04365-2026", "O04365", "experiments/external_sources/chemistry/snapshots/goldbook-terms/O04365.json", "sha256:5413171bfaa9152ff9a6a2dee0c79a2ec3e31a4d1efbfff0f8c76804c7fdb06e"),
    "SFT-CHEM-REDOX-COUPLING-001": ("redox-coupling-iupac-composite", "IUPAC-GOLD-BOOK-REDOX-COMPOSITE-2026", "O04362", "experiments/external_sources/chemistry/snapshots/goldbook-terms/O04362.json", "sha256:9e367d54ae7e7f9e5a40366f9298b1c8dfffbac4677847f60458b78e7e16fc68"),
    "SFT-CHEM-ELECTROCHEM-CELL-001": ("electrochemical-cell-iupac-composite", "IUPAC-GOLD-BOOK-ELECTROCHEMICAL-CELL-COMPOSITE-2026", "09058", "experiments/external_sources/chemistry/snapshots/goldbook-terms/09058.json", "sha256:0016d0976a51c44b0208458810ad455a459f988c7573d186293edff0aea33d68"),
}


def validate_pre_source_seal() -> None:
    if hash_file(ROOT / DERIVATION_PATH) != DERIVATION_HASH:
        raise ValueError("target-blind redox derivation changed after its pre-source seal")
    seal = json.loads((ROOT / PRE_SOURCE_SEAL_PATH).read_text(encoding="utf-8"))
    claimed_hash = seal.pop("sealed_payload_hash", None)
    if claimed_hash != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(seal) != PRE_SOURCE_PAYLOAD_HASH:
        raise ValueError("redox pre-source seal payload is invalid")
    expected = [{"claim_id": row.claim_id, "exact_result": row.exact_result, "predicted_observation_label": row.predicted_observation_label} for row in REDOX_BLUEPRINTS]
    if seal.get("claim_predictions") != expected:
        raise ValueError("redox predictions differ from the pre-source seal")
    if seal.get("external_source_identities_selected") is not False or seal.get("external_target_content_opened") is not False:
        raise ValueError("redox derivation was not sealed before source selection")


def _bind(blueprint) -> EmpiricalChemistrySpec:
    target_id, source_id, code, snapshot_path, digest = SOURCE_RECORDS[blueprint.claim_id]
    return EmpiricalChemistrySpec(
        claim_id=blueprint.claim_id, title=blueprint.title, statement=blueprint.statement,
        dependencies=blueprint.dependencies, generation_rule=blueprint.generation_rule,
        grammar_boundary=blueprint.grammar_boundary, dimensions=blueprint.dimensions,
        exact_result=blueprint.exact_result, induction_base=blueprint.induction_base,
        induction_step=blueprint.induction_step, exclusions=blueprint.exclusions,
        operational_witnesses=blueprint.operational_witnesses, experiment_id=blueprint.experiment_id,
        expected_observation_label=blueprint.predicted_observation_label,
        target_rows=(ChemistryTargetReference(target_id, source_id, f"official IUPAC source set anchored at {code}", snapshot_path, digest),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition=blueprint.falsification_condition,
    )


validate_pre_source_seal()
REDOX_BATCH_1_SPECS = tuple(_bind(row) for row in REDOX_BLUEPRINTS)
for _spec in REDOX_BATCH_1_SPECS:
    _spec.validate()

__all__ = ("REDOX_BATCH_1_SPECS", "validate_pre_source_seal")
