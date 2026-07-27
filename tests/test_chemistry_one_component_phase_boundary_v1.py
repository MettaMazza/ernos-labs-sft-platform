import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.one_component_phase_boundary_batch_v1 import ONE_COMPONENT_PHASE_BOUNDARY_SPEC
from sft.chemistry.one_component_phase_boundary_law_v1 import (
    FiniteOneComponentBoundary, OneComponentCoexistencePoint, coexistence_exchange_balance,
    common_support_replication_preserves_boundary, is_ordered_coexistence_successor,
    one_component_two_phase_degree_support_is_one,
)
from sft.chemistry.one_component_phase_boundary_validation_v1 import (
    OneComponentPhaseBoundaryValidator, _identities, _prediction_map, _source_rows,
    exact_phase_boundary_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def point(temperature, pressure, first_exchange=5, second_exchange=5):
    return OneComponentCoexistencePoint(
        HeldLabel("chemical-component", "a"), HeldLabel("chemical-phase", "liquid"), HeldLabel("chemical-phase", "vapor"),
        PositiveCount(temperature), PositiveCount(pressure), PositiveCount(first_exchange), PositiveCount(second_exchange),
    )


def test_exchange_balance_and_single_degree_support():
    state = point(3, 2)
    assert isinstance(coexistence_exchange_balance(state).separation, EmptyOne)
    assert one_component_two_phase_degree_support_is_one(state)


def test_unbalanced_or_nonordered_boundary_halts():
    with pytest.raises(InadmissibleExactValue):
        FiniteOneComponentBoundary((point(3, 2, 5, 6),))
    with pytest.raises(InadmissibleExactValue):
        FiniteOneComponentBoundary((point(3, 2), point(5, 1)))


def test_ordered_successor_and_replication_preserve_boundary():
    first, second = point(3, 2), point(5, 4, 7, 7)
    assert is_ordered_coexistence_successor(first, second)
    assert common_support_replication_preserves_boundary(FiniteOneComponentBoundary((first, second)), PositiveCount(6))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(ONE_COMPONENT_PHASE_BOUNDARY_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(ONE_COMPONENT_PHASE_BOUNDARY_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_15_rows_and_no_values():
    rows = _identities(ROOT)
    forbidden = {"component_orgnum", "temperature_K_external_inscription", "pressure_kPa_external_inscription", "pressure_uncertainty", "target_payload_hash"}
    assert len(rows) == 15
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in ("temperature_K_external_inscription", "pressure_kPa_external_inscription", "pressure_uncertainty"):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")})
    assert len(_prediction_map(execution.output)) == 15


def test_complete_external_vector_retains_all_points_and_successions():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-012-one-component-phase-boundary-v1/one-component-phase-boundary-primary-records-v1.json").read_text())
    analysis = exact_phase_boundary_analysis(_source_rows(ROOT), primary)
    assert analysis["all_15_points_retained"]
    assert analysis["all_three_complete_datasets_retained"]
    assert analysis["both_compounds_and_parallel_component_four_datasets_retained"]
    assert analysis["all_12_adjacent_successions_exactly_coordered"]
    assert analysis["complete_parent_source_preserved"]
    assert analysis["no_imported_curve_equation_interpolation_or_fit"]


def test_postseal_validator_preserves_values_rows_and_controls():
    result = OneComponentPhaseBoundaryValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 25
