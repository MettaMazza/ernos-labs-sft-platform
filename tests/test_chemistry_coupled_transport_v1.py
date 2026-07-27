import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.coupled_transport_batch_v1 import COUPLED_TRANSPORT_SPEC, PRIMARY_PATH
from sft.chemistry.coupled_transport_law_v1 import CoupledTransportAccount, common_event_replication_preserves_relation, forced_coupled_transport
from sft.chemistry.coupled_transport_validation_v1 import CoupledTransportValidator, _identities, _prediction_map, _source_rows, exact_coupled_transport_analysis, prediction_program_document
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(count=2, reverse=False):
    return CoupledTransportAccount(
        tuple(HeldLabel("chemical-component", f"component-{i}") for i in range(1, count + 1)), HeldLabel("chemical-phase", "liquid"),
        tuple(HeldLabel("transport-carrier", name) for name in ("mass", "heat", "charge")),
        PositiveCount(5 if reverse else 4), PositiveCount(4 if reverse else 5),
        (PositiveCount(2), PositiveCount(3), PositiveCount(5)), PositiveCount(7), PositiveCount(11), PositiveCount(2),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def test_complete_triad_projections_orientations_and_responses():
    relation = forced_coupled_transport(account())
    assert tuple(row.label for row in relation.pairwise_projections) == ("mass-heat", "mass-charge", "heat-charge")
    assert relation.orientations != forced_coupled_transport(account(reverse=True)).orientations
    assert tuple(row.fraction for row in relation.response_support) == tuple(PositiveRatio.from_pair(value, 22).fraction for value in (14, 21, 35))


def test_replication_and_composition_carriers():
    assert common_event_replication_preserves_relation(account(3), PositiveCount(6))
    assert forced_coupled_transport(account(2)).carrier_topology.label.startswith("binary-")
    assert forced_coupled_transport(account(3)).carrier_topology.label.startswith("ternary-")


def test_incomplete_triad_nonadjacent_and_wrong_order_halt():
    with pytest.raises(InadmissibleExactValue):
        CoupledTransportAccount((HeldLabel("chemical-component", "a"),), HeldLabel("chemical-phase", "liquid"), (HeldLabel("transport-carrier", "mass"), HeldLabel("transport-carrier", "heat")), PositiveCount(2), PositiveCount(3), (PositiveCount(1), PositiveCount(1)), PositiveCount(1), PositiveCount(1), PositiveCount(1), (EmptyOne(),))
    with pytest.raises(InadmissibleExactValue):
        CoupledTransportAccount((HeldLabel("chemical-component", "a"),), HeldLabel("chemical-phase", "liquid"), tuple(HeldLabel("transport-carrier", name) for name in ("mass", "heat", "charge")), PositiveCount(2), PositiveCount(4), (PositiveCount(1), PositiveCount(1), PositiveCount(1)), PositiveCount(1), PositiveCount(1), PositiveCount(1), (EmptyOne(),))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(COUPLED_TRANSPORT_SPEC, "sha256:" + "d" * 64); candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates); closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(COUPLED_TRANSPORT_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT); forbidden = {"response_role", "property_name", "measurement_method", "coupled_response_external_inscription", "target_payload_hash"}
    assert len(rows) == 232 and all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT); rendered = json.dumps(document, sort_keys=True)
    assert "coupled_response_external_inscription" not in rendered and "measurement_method" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")})
    assert len(_prediction_map(execution.output)) == 232


def test_complete_external_vector_retains_every_pair_source_and_companion():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text()); analysis = exact_coupled_transport_analysis(_source_rows(ROOT), primary)
    assert analysis["all_232_records_retained"] and analysis["all_three_pairwise_surfaces_retained"]
    assert analysis["all_response_roles_retained"] and analysis["all_four_property_families_retained"]
    assert analysis["all_137_binary_95_ternary_records_retained"] and analysis["all_15_coupled_datasets_complete"]
    assert analysis["all_five_methods_retained"] and analysis["all_six_absent_conditions_are_EmptyOne"]
    assert analysis["mass_heat_surface_is_thermal_forcing_method"] and analysis["complete_three_sources_and_companions_preserved"]
    assert analysis["companions_excluded_from_measurements"] and analysis["no_imported_matrix_continuum_fitted_law_or_selection"]


def test_postseal_validator_preserves_rows_and_controls():
    result = CoupledTransportValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True and result.all_rows_preserved is True and len(result.measurements) == 240
