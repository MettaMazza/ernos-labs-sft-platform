import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.viscous_transport_batch_v1 import VISCOUS_TRANSPORT_SPEC
from sft.chemistry.viscous_transport_law_v1 import ViscousChemicalAccount, common_exchange_replication_preserves_relation, external_viscosity_magnitude, forced_viscous_transport
from sft.chemistry.viscous_transport_validation_v1 import ViscousTransportValidator, _identities, _prediction_map, _source_rows, exact_viscous_transport_analysis, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id

ROOT = Path(__file__).resolve().parents[1]


def account(count=2, reverse=False):
    return ViscousChemicalAccount(
        tuple(HeldLabel("chemical-component", f"component-{i}") for i in range(1, count + 1)), HeldLabel("chemical-phase", "liquid"),
        PositiveCount(5 if reverse else 4), PositiveCount(4 if reverse else 5), PositiveCount(3), PositiveCount(7), PositiveCount(5),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def test_composition_carriers_orientation_and_density():
    assert forced_viscous_transport(account(1)).carrier.label.startswith("pure-")
    assert forced_viscous_transport(account(2)).carrier.label.startswith("binary-")
    assert forced_viscous_transport(account(3)).carrier.label.startswith("ternary-")
    assert forced_viscous_transport(account()).orientation.label == "toward-later-generated-layer"
    assert forced_viscous_transport(account(reverse=True)).orientation.label == "toward-earlier-generated-layer"
    assert forced_viscous_transport(account()).exchange_density.fraction == PositiveRatio.from_pair(21, 5).fraction


def test_replication_and_external_magnitude():
    assert common_exchange_replication_preserves_relation(account(3), PositiveCount(6))
    assert external_viscosity_magnitude("0.00125").fraction == PositiveRatio.from_pair(1, 800).fraction


def test_nonadjacent_and_negative_viscosity_halt():
    with pytest.raises(InadmissibleExactValue):
        ViscousChemicalAccount((HeldLabel("chemical-component", "a"),), HeldLabel("chemical-phase", "liquid"), PositiveCount(2), PositiveCount(4), PositiveCount(1), PositiveCount(1), PositiveCount(1), (EmptyOne(),))
    with pytest.raises(InadmissibleExactValue): external_viscosity_magnitude("-1")


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(VISCOUS_TRANSPORT_SPEC, "sha256:" + "d" * 64); candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates); closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(VISCOUS_TRANSPORT_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT); forbidden = {"component_orgnums", "measurement_method", "viscosity_Pa_s_external_inscription", "target_payload_hash"}
    assert len(rows) == 425 and all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT); rendered = json.dumps(document, sort_keys=True)
    assert "viscosity_Pa_s_external_inscription" not in rendered and "measurement_method" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")})
    assert len(_prediction_map(execution.output)) == 425


def test_complete_external_vector_retains_every_source_and_companion():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-017-viscous-transport-v1/viscous-transport-primary-records-v1.json").read_text())
    analysis = exact_viscous_transport_analysis(_source_rows(ROOT), primary)
    assert analysis["all_425_records_retained"] and analysis["all_11_pure_364_binary_50_ternary_records_retained"]
    assert analysis["all_eight_viscosity_datasets_complete"] and analysis["all_five_measurement_methods_retained"]
    assert analysis["all_38_absent_condition_coordinates_are_EmptyOne"] and analysis["complete_three_sources_and_companions_preserved"]
    assert analysis["non_viscosity_companions_excluded_from_measurements"] and analysis["no_imported_constitutive_continuum_fitted_law_or_selection"]


def test_postseal_validator_preserves_rows_and_controls():
    result = ViscousTransportValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True and result.all_rows_preserved is True and len(result.measurements) == 434
