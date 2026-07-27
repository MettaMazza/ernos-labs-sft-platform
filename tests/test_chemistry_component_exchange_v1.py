import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.component_exchange_batch_v1 import COMPONENT_EXCHANGE_SPEC
from sft.chemistry.component_exchange_law_v1 import (
    ComponentAdditionAccount,
    common_context_successor_preserves_exchange,
    component_exchange_relation,
)
from sft.chemistry.component_exchange_validation_v1 import (
    ComponentExchangeValidator,
    _identities,
    _prediction_map,
    _source_rows,
    exact_component_exchange_analysis,
    prediction_program_document,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(phase, energy, distinctions, component="held-component", environment="held-environment"):
    return ComponentAdditionAccount(
        HeldLabel("chemical-component", component),
        HeldLabel("chemical-phase", phase),
        HeldLabel("chemical-environment", environment),
        PositiveRatio.from_pair(energy, 3),
        PositiveCount(distinctions),
    )


def test_exact_component_accounts_force_direction_and_equilibrium():
    directed = component_exchange_relation(account("liquid", 5, 2), account("gas", 8, 3))
    equilibrium = component_exchange_relation(account("liquid", 5, 2), account("gas", 5, 2))
    assert directed.orientation.label == "toward-first-phase"
    assert directed.energy_separation == PositiveRatio.from_pair(1, 1)
    assert directed.distinction_separation == PositiveCount(1)
    assert equilibrium.orientation.label == "equilibrium"
    assert isinstance(equilibrium.energy_separation, EmptyOne)
    assert isinstance(equilibrium.distinction_separation, EmptyOne)


def test_changed_identity_environment_or_crossed_account_halts():
    with pytest.raises(InadmissibleExactValue):
        component_exchange_relation(account("liquid", 5, 2), account("gas", 5, 2, component="other"))
    with pytest.raises(InadmissibleExactValue):
        component_exchange_relation(account("liquid", 5, 2), account("gas", 5, 2, environment="other"))
    with pytest.raises(InadmissibleExactValue):
        component_exchange_relation(account("liquid", 5, 4), account("gas", 8, 2))


def test_common_context_successor_preserves_relation():
    assert common_context_successor_preserves_exchange(
        account("liquid", 5, 2),
        account("gas", 8, 3),
        PositiveRatio.from_pair(7, 5),
        PositiveCount(2),
    )


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(COMPONENT_EXCHANGE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(
        COMPONENT_EXCHANGE_SPEC
    )
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_74_rows_and_no_values():
    rows = _identities(ROOT)
    forbidden = {
        "ordered_component_orgnums",
        "pressure_kPa_external_inscription",
        "temperature_K_external_inscription",
        "liquid_variable_component_part_external_inscription",
        "gas_variable_component_part_external_inscription",
        "target_payload_hash",
    }
    assert len(rows) == 74
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in (
        "pressure_kPa_external_inscription",
        "temperature_K_external_inscription",
        "liquid_variable_component_part_external_inscription",
        "gas_variable_component_part_external_inscription",
    ):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 74


def test_complete_external_vector_retains_all_systems_rows_and_endpoints():
    primary = json.loads(
        (
            ROOT
            / "experiments/external_sources/chemistry/snapshots/thermo-008-component-exchange-v1/component-exchange-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_component_exchange_analysis(_source_rows(ROOT), primary)
    assert analysis["all_74_rows_retained"]
    assert analysis["all_four_systems_retained"]
    assert analysis["all_rows_share_fixed_101_3_kPa_environment"]
    assert analysis["equal_component_account_does_not_require_equal_bulk_composition"]
    assert analysis["both_external_enrichment_orientations_retained"]
    assert analysis["system_one_composition_crossing_retained"]
    assert analysis["all_eight_unmatched_source_endpoints_preserved"]


def test_postseal_validator_preserves_values_rows_and_controls():
    result = ComponentExchangeValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 83
