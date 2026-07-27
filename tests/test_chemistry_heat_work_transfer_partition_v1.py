import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.heat_work_transfer_partition_batch_v1 import HEAT_WORK_TRANSFER_PARTITION_SPEC
from sft.chemistry.heat_work_transfer_partition_law_v1 import (
    append_transfer_preserves_partition, chemical_transfer_record, partition_chemical_transfers,
    transfer_class_from_observation,
)
from sft.chemistry.heat_work_transfer_partition_validation_v1 import (
    HeatWorkTransferPartitionValidator, _prediction_map, exact_heat_work_analysis,
    prediction_program_document,
)
from sft.chemistry.internal_energy_composition_validation_v1 import VALUE_COLUMNS, _source_rows
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def record(carrier: str, numerator: int, denominator: int = 1):
    return chemical_transfer_record(
        HeldLabel("chemical-boundary", "held-boundary"), HeldLabel("chemical-path", "held-path"),
        HeldLabel("energy-transfer-orientation", "into-held-support"),
        HeldLabel("transfer-carrier-observation", carrier), PositiveRatio.from_pair(numerator, denominator),
    )


def test_carrier_observation_forces_heat_and_work_classes() -> None:
    heat = transfer_class_from_observation(HeldLabel("transfer-carrier-observation", "carrier-label-closed-by-receiving-macro-observation"))
    work = transfer_class_from_observation(HeldLabel("transfer-carrier-observation", "organized-source-response-label-retained"))
    assert heat.label == "heat-transfer" and work.label == "work-transfer"
    with pytest.raises(InadmissibleExactValue):
        transfer_class_from_observation(HeldLabel("transfer-carrier-observation", "arbitrary-class"))


def test_exact_partition_retains_classes_and_EmptyOne_absence() -> None:
    first = record("carrier-label-closed-by-receiving-macro-observation", 2, 3)
    second = record("carrier-label-closed-by-receiving-macro-observation", 5, 4)
    third = record("organized-source-response-label-retained", 7, 5)
    heat_only = partition_chemical_transfers((first, second))
    complete = partition_chemical_transfers((first, second, third))
    assert heat_only.heat_total == PositiveRatio.from_pair(23, 12)
    assert isinstance(heat_only.work_total, EmptyOne)
    assert complete.work_total == PositiveRatio.from_pair(7, 5)
    assert complete.complete_transfer_total == PositiveRatio.from_pair(199, 60)


def test_append_only_transfer_successor_preserves_prior_path() -> None:
    prior = (
        record("carrier-label-closed-by-receiving-macro-observation", 2, 3),
        record("carrier-label-closed-by-receiving-macro-observation", 5, 4),
    )
    extension = record("organized-source-response-label-retained", 7, 5)
    assert append_transfer_preserves_partition(prior, extension)


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(HEAT_WORK_TRANSFER_PARTITION_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(HEAT_WORK_TRANSFER_PARTITION_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_value_free_for_heat_work() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json").read_text())
    forbidden = set(VALUE_COLUMNS) | {"snapshot_hash", "target_payload", "target_payload_hash"}
    assert len(document["rows"]) == 13
    assert all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_complete_and_has_no_target_values() -> None:
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in ("isobaric-heat-capacity-joule-per-mole-kelvin", "volume-litre-per-mole", "enthalpy-kilojoule-per-mole", "internal-energy-kilojoule-per-mole"):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 13


def test_complete_external_calorimetric_and_work_vectors_are_exact() -> None:
    analysis = exact_heat_work_analysis(_source_rows(ROOT))
    assert len(analysis["calorimetric_heat_capacity_values"]) == 13
    assert len(analysis["pressure_volume_work_values_kilojoule_per_mole"]) == 13
    assert len(analysis["state_record_work_values_kilojoule_per_mole"]) == 13
    assert all(bool(value) for key, value in analysis.items() if not isinstance(value, tuple))


def test_postseal_validator_preserves_all_rows_values_and_controls() -> None:
    result = HeatWorkTransferPartitionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 22
