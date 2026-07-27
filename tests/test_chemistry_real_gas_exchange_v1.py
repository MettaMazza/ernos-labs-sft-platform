import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.real_gas_exchange_batch_v1 import REAL_GAS_EXCHANGE_SPEC
from sft.chemistry.real_gas_exchange_law_v1 import (
    GasComponentExchangeAccount,
    GasCompositionCoordinate,
    exact_fugacity_equivalent,
    phase_exchange_relation,
    real_gas_interaction_relation,
    replicated_support_preserves_gas_law,
)
from sft.chemistry.real_gas_exchange_validation_v1 import (
    RealGasExchangeValidator,
    _identities,
    _prediction_map,
    _source_rows,
    exact_real_gas_analysis,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(accessible, reference, independent):
    return GasComponentExchangeAccount(
        HeldLabel("chemical-component", "a"),
        HeldLabel("chemical-phase", "gas-mixture"),
        HeldLabel("chemical-environment", "held-state"),
        (
            GasCompositionCoordinate(HeldLabel("chemical-component", "a"), PositiveRatio.from_pair(3, 5)),
            GasCompositionCoordinate(HeldLabel("chemical-component", "b"), PositiveRatio.from_pair(2, 5)),
        ),
        PositiveCount(accessible),
        PositiveCount(reference),
        PositiveCount(independent),
    )


def test_exact_fugacity_equivalent_interaction_and_phase_balance():
    state = account(6, 10, 8)
    assert exact_fugacity_equivalent(state).fraction == PositiveRatio.from_pair(3, 5).fraction
    assert real_gas_interaction_relation(state).relation.label == "interaction-restricted-support"
    balanced = phase_exchange_relation(state, PositiveCount(6))
    assert balanced.relation.label == "balanced"
    assert isinstance(balanced.support_separation, EmptyOne)


def test_inadmissible_gas_support_and_composition_halt():
    with pytest.raises(InadmissibleExactValue):
        account(11, 10, 8)
    with pytest.raises(InadmissibleExactValue):
        GasCompositionCoordinate(HeldLabel("chemical-component", "a"), PositiveRatio.from_pair(6, 5))


def test_common_support_replication_preserves_every_relation():
    assert replicated_support_preserves_gas_law(account(6, 10, 8), PositiveCount(6), PositiveCount(7))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(REAL_GAS_EXCHANGE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(
        REAL_GAS_EXCHANGE_SPEC
    )
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_94_rows_and_no_values():
    rows = _identities(ROOT)
    forbidden = {
        "ordered_component_orgnums",
        "complete_component_records",
        "pressure_kPa_external_inscription",
        "gas_component_mole_fraction_external_inscription",
        "condition_and_liquid_composition_coordinates",
        "pressure_uncertainty",
        "target_payload_hash",
    }
    assert len(rows) == 94
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in (
        "pressure_kPa_external_inscription",
        "gas_component_mole_fraction_external_inscription",
        "condition_and_liquid_composition_coordinates",
        "pressure_uncertainty",
    ):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 94


def test_complete_external_vector_retains_all_states_and_raw_records():
    primary = json.loads(
        (
            ROOT
            / "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1/real-gas-equilibrium-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_real_gas_analysis(_source_rows(ROOT), primary)
    assert analysis["all_94_equilibrium_states_retained"]
    assert analysis["all_seven_pressure_datasets_retained"]
    assert analysis["all_three_binary_component_pairs_retained"]
    assert analysis["all_59_paired_gas_compositions_retained"]
    assert analysis["all_35_pressure_only_states_retained"]
    assert analysis["complete_raw_source_surface_preserved"]
    assert analysis["no_correlated_fitted_or_imported_model_value_used"]


def test_postseal_validator_preserves_values_rows_and_controls():
    result = RealGasExchangeValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 105
