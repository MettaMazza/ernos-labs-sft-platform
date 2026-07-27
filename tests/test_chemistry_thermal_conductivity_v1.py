import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.thermal_conductivity_batch_v1 import PRIMARY_PATH, THERMAL_CONDUCTIVITY_SPEC
from sft.chemistry.thermal_conductivity_law_v1 import (
    ThermalConductionAccount, common_transfer_replication_preserves_relation,
    external_thermal_conductivity_magnitude, forced_thermal_conductivity,
)
from sft.chemistry.thermal_conductivity_validation_v1 import (
    ThermalConductivityValidator, _identities, _prediction_map, _source_rows,
    exact_thermal_conductivity_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(count: int = 2, reverse: bool = False) -> ThermalConductionAccount:
    return ThermalConductionAccount(
        tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, count + 1)),
        HeldLabel("chemical-phase", "liquid"), PositiveCount(4), PositiveCount(5),
        PositiveCount(3 if reverse else 7), PositiveCount(7 if reverse else 3),
        PositiveCount(5), PositiveCount(11), PositiveCount(7), PositiveCount(2),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def test_composition_carriers_orientation_and_response():
    assert forced_thermal_conductivity(account(1)).carrier.label.startswith("pure-")
    assert forced_thermal_conductivity(account(2)).carrier.label.startswith("binary-")
    assert forced_thermal_conductivity(account(3)).carrier.label.startswith("ternary-")
    assert forced_thermal_conductivity(account()).orientation != forced_thermal_conductivity(account(reverse=True)).orientation
    assert forced_thermal_conductivity(account()).transfer_response.fraction == PositiveRatio.from_pair(55, 56).fraction


def test_replication_and_external_magnitude():
    assert common_transfer_replication_preserves_relation(account(3), PositiveCount(6))
    assert external_thermal_conductivity_magnitude("0.125").fraction == PositiveRatio.from_pair(1, 8).fraction


def test_nonadjacent_equal_order_and_negative_conductivity_halt():
    with pytest.raises(InadmissibleExactValue):
        ThermalConductionAccount(
            (HeldLabel("chemical-component", "a"),), HeldLabel("chemical-phase", "liquid"),
            PositiveCount(2), PositiveCount(4), PositiveCount(7), PositiveCount(3), PositiveCount(1),
            PositiveCount(1), PositiveCount(1), PositiveCount(1), (EmptyOne(),),
        )
    with pytest.raises(InadmissibleExactValue):
        ThermalConductionAccount(
            (HeldLabel("chemical-component", "a"),), HeldLabel("chemical-phase", "liquid"),
            PositiveCount(2), PositiveCount(3), PositiveCount(7), PositiveCount(7), PositiveCount(1),
            PositiveCount(1), PositiveCount(1), PositiveCount(1), (EmptyOne(),),
        )
    with pytest.raises(InadmissibleExactValue):
        external_thermal_conductivity_magnitude("-1")


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(THERMAL_CONDUCTIVITY_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(THERMAL_CONDUCTIVITY_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT)
    forbidden = {"component_orgnums", "property_phase", "measurement_method", "thermal_conductivity_W_m_K_external_inscription", "target_payload_hash"}
    assert len(rows) == 655 and all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "thermal_conductivity_W_m_K_external_inscription" not in rendered and "measurement_method" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")}
    )
    assert len(_prediction_map(execution.output)) == 655


def test_complete_external_vector_retains_every_source_and_companion():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_thermal_conductivity_analysis(_source_rows(ROOT), primary)
    assert analysis["all_655_records_retained"] and analysis["all_123_pure_273_binary_259_ternary_records_retained"]
    assert analysis["all_51_gas_571_liquid_33_crystal_records_retained"]
    assert analysis["all_37_conductivity_datasets_complete"] and analysis["all_three_measurement_methods_retained"]
    assert analysis["complete_three_sources_and_companions_preserved"]
    assert analysis["non_conductivity_companions_excluded_from_measurements"]
    assert analysis["no_imported_constitutive_continuum_fitted_law_or_selection"]


def test_postseal_validator_preserves_rows_and_controls():
    result = ThermalConductivityValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True and result.all_rows_preserved is True and len(result.measurements) == 665
