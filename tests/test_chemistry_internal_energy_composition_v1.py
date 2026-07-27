import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.internal_energy_composition_batch_v1 import INTERNAL_ENERGY_COMPOSITION_SPEC
from sft.chemistry.internal_energy_composition_law_v1 import (
    EXACT_RESULT, ChemicalInternalEnergyState, InternalEnergyPart,
    append_energy_part_preserves_prior_composition, compose_internal_energy_parts,
    compose_oriented_internal_energy_steps, exact_internal_energy_relation,
)
from sft.chemistry.internal_energy_composition_validation_v1 import (
    InternalEnergyCompositionValidator, VALUE_COLUMNS, _prediction_map, _source_rows,
    exact_internal_energy_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def state(label: str, numerator: int) -> ChemicalInternalEnergyState:
    return ChemicalInternalEnergyState(
        HeldLabel("chemical-composition", "water"), HeldLabel("molecular-state", label),
        HeldLabel("phase-identity", "held-phase"), HeldLabel("held-environment", "one-bar"),
        PositiveRatio.from_pair(numerator, 3),
    )


def test_exact_positive_parts_compose_without_fit() -> None:
    parts = (
        InternalEnergyPart(HeldLabel("internal-energy-part", "first"), PositiveRatio.from_pair(2, 3)),
        InternalEnergyPart(HeldLabel("internal-energy-part", "second"), PositiveRatio.from_pair(5, 4)),
    )
    assert compose_internal_energy_parts(parts) == PositiveRatio.from_pair(23, 12)
    assert append_energy_part_preserves_prior_composition(
        parts, InternalEnergyPart(HeldLabel("internal-energy-part", "third"), PositiveRatio.from_pair(7, 5)),
    )


def test_orientation_is_held_and_equality_is_structural() -> None:
    first, second = state("first", 5), state("second", 8)
    rise = exact_internal_energy_relation(first, second)
    fall = exact_internal_energy_relation(second, first)
    equal = exact_internal_energy_relation(first, first)
    assert rise.orientation.label == "internal-energy-rise" and rise.exact_positive_magnitude == PositiveRatio.from_pair(1, 1)
    assert fall.orientation.label == "internal-energy-fall" and fall.exact_positive_magnitude == PositiveRatio.from_pair(1, 1)
    assert equal.orientation.label == "internal-energy-equal" and isinstance(equal.exact_positive_magnitude, EmptyOne)


def test_same_direction_steps_compose_and_opposed_steps_halt() -> None:
    first, second, third = state("first", 5), state("second", 8), state("third", 14)
    one = exact_internal_energy_relation(first, second)
    two = exact_internal_energy_relation(second, third)
    assert compose_oriented_internal_energy_steps((one, two)) == exact_internal_energy_relation(first, third)
    with pytest.raises(InadmissibleExactValue):
        compose_oriented_internal_energy_steps((one, exact_internal_energy_relation(third, second)))


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(INTERNAL_ENERGY_COMPOSITION_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(INTERNAL_ENERGY_COMPOSITION_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = set(VALUE_COLUMNS) | {"snapshot_hash", "target_payload", "target_payload_hash"}
    assert document["all_returned_temperatures_phases_and_property_values_absent"] is True
    assert len(document["rows"]) == 13
    assert all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "internal-energy-kilojoule-per-mole" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 13


def test_complete_external_internal_energy_path_is_exact() -> None:
    rows = _source_rows(ROOT)
    analysis = exact_internal_energy_analysis(rows)
    assert len(analysis["internal_energy_values"]) == 13
    assert len(analysis["adjacent_exact_positive_steps"]) == 12
    assert all(bool(value) for key, value in analysis.items() if key not in {"internal_energy_values", "adjacent_exact_positive_steps"})


def test_postseal_validator_preserves_all_rows_values_and_controls() -> None:
    result = InternalEnergyCompositionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 21
