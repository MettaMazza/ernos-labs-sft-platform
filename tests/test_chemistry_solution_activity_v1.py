import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.solution_activity_batch_v1 import SOLUTION_ACTIVITY_SPEC
from sft.chemistry.solution_activity_law_v1 import (
    SolutionActivityAccount,
    SolutionCompositionCoordinate,
    exact_relative_activity,
    nonideal_composition_relation,
    replicated_support_preserves_activity_and_relation,
)
from sft.chemistry.solution_activity_validation_v1 import (
    SolutionActivityValidator,
    _identities,
    _prediction_map,
    _source_rows,
    exact_solution_activity_analysis,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(accessible, reference, independent):
    return SolutionActivityAccount(
        HeldLabel("chemical-component", "water"),
        HeldLabel("chemical-phase", "liquid"),
        HeldLabel("chemical-environment", "held"),
        (
            SolutionCompositionCoordinate(HeldLabel("chemical-component", "a"), PositiveRatio.from_pair(3, 2)),
            SolutionCompositionCoordinate(HeldLabel("chemical-component", "b"), EmptyOne()),
        ),
        PositiveCount(accessible),
        PositiveCount(reference),
        PositiveCount(independent),
    )


def test_exact_activity_and_nonideal_relations():
    restricted = account(6, 10, 8)
    assert exact_relative_activity(restricted).fraction == PositiveRatio.from_pair(3, 5).fraction
    assert nonideal_composition_relation(restricted).relation.label == "interaction-restricted"
    assert nonideal_composition_relation(account(8, 10, 8)).relation.label == "independent"
    assert nonideal_composition_relation(account(9, 10, 8)).relation.label == "interaction-expanded"


def test_absence_is_EmptyOne_and_overfull_support_halts():
    assert isinstance(account(6, 10, 8).composition[1].coordinate, EmptyOne)
    with pytest.raises(InadmissibleExactValue):
        account(11, 10, 8)


def test_support_replication_preserves_activity_and_relation():
    assert replicated_support_preserves_activity_and_relation(account(6, 10, 8), PositiveCount(7))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(SOLUTION_ACTIVITY_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(
        SOLUTION_ACTIVITY_SPEC
    )
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_204_rows_and_no_values():
    rows = _identities(ROOT)
    forbidden = {
        "ordered_component_orgnums",
        "temperature_K_external_inscription",
        "relative_water_activity_external_inscription",
        "composition_interface_entries",
        "activity_uncertainty",
        "target_payload_hash",
    }
    assert len(rows) == 204
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in (
        "temperature_K_external_inscription",
        "relative_water_activity_external_inscription",
        "external_molality_inscription",
        "activity_uncertainty",
    ):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 204


def test_complete_external_vector_retains_all_rows_and_absence_boundaries():
    primary = json.loads(
        (
            ROOT
            / "experiments/external_sources/chemistry/snapshots/thermo-009-solution-activity-v1/solution-activity-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_solution_activity_analysis(_source_rows(ROOT), primary)
    assert analysis["all_204_rows_retained"]
    assert analysis["all_nine_datasets_retained"]
    assert analysis["all_rows_share_fixed_298_15_K_environment"]
    assert analysis["all_activities_exact_positive_parts_of_One"]
    assert analysis["all_68_absence_rows_and_coordinates_translated_to_EmptyOne"]
    assert analysis["complete_binary_and_ternary_rows_retained"]
    assert analysis["no_correlated_or_fitted_model_value_used"]


def test_postseal_validator_preserves_values_rows_and_controls():
    result = SolutionActivityValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 213
