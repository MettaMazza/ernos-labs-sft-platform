import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.colligative_response_batch_v1 import COLLIGATIVE_RESPONSE_SPEC
from sft.chemistry.colligative_response_law_v1 import (
    ColligativeParticleAccount, common_particle_replication_preserves_orientation,
    exact_response_replication_preserves_order, exact_response_separation, forced_colligative_orientation,
)
from sft.chemistry.colligative_response_validation_v1 import (
    ColligativeResponseValidator, _identities, _prediction_map, _source_rows,
    exact_colligative_analysis, prediction_program_document,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(response_class, present=True):
    return ColligativeParticleAccount(
        HeldLabel("chemical-component", "solvent"), HeldLabel("chemical-component", "solute"),
        HeldLabel("colligative-response", response_class), PositiveRatio.from_pair(1, 5) if present else EmptyOne(),
        PositiveCount(7), PositiveCount(3),
    )


def test_three_orientations_and_pure_solvent_boundary():
    assert forced_colligative_orientation(account("boiling")).relation.label.startswith("temperature-support-expanded")
    assert forced_colligative_orientation(account("freezing")).relation.label.startswith("temperature-support-reduced")
    assert forced_colligative_orientation(account("osmotic")).relation.label.startswith("pressure-support-directed")
    assert isinstance(forced_colligative_orientation(account("boiling", False)).composition_boundary, EmptyOne)


def test_invalid_identity_halts():
    with pytest.raises(InadmissibleExactValue):
        ColligativeParticleAccount(HeldLabel("chemical-component", "same"), HeldLabel("chemical-component", "same"), HeldLabel("colligative-response", "boiling"), EmptyOne(), PositiveCount(2), PositiveCount(2))


def test_exact_separation_and_replication():
    result = exact_response_separation(PositiveRatio.from_pair(7, 3), PositiveRatio.from_pair(8, 3))
    assert result.separation.fraction == PositiveRatio.from_pair(1, 3).fraction
    assert common_particle_replication_preserves_orientation(account("osmotic"), PositiveCount(6))
    assert exact_response_replication_preserves_order(PositiveRatio.from_pair(7, 3), PositiveRatio.from_pair(8, 3), PositiveCount(6))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(COLLIGATIVE_RESPONSE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(COLLIGATIVE_RESPONSE_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT)
    forbidden = {"component_orgnums", "composition_external_inscription", "response_external_inscription", "target_payload_hash"}
    assert len(rows) == 276
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "response_external_inscription" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")})
    assert len(_prediction_map(execution.output)) == 276


def test_complete_external_vector_retains_all_three_classes():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-014-colligative-response-v1/colligative-response-primary-records-v1.json").read_text())
    analysis = exact_colligative_analysis(_source_rows(ROOT), primary)
    assert analysis["all_276_records_retained"]
    assert analysis["all_144_boiling_37_freezing_95_osmotic_records_retained"]
    assert analysis["all_28_datasets_complete"]
    assert analysis["sole_absent_coordinate_is_EmptyOne_reference"]
    assert analysis["complete_three_sources_preserved"]
    assert analysis["no_imported_response_equation_constant_or_fit"]


def test_postseal_validator_preserves_rows_and_controls():
    result = ColligativeResponseValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 285
