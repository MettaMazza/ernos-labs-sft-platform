import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.phase_rule_batch_v1 import PHASE_RULE_SPEC
from sft.chemistry.phase_rule_law_v1 import PhaseRuleAccount, independent_degree_support, joint_component_phase_successor_preserves_degree_support
from sft.chemistry.phase_rule_validation_v1 import PhaseRuleValidator, _identities, _prediction_map, _source_rows, exact_phase_rule_analysis, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(components, phases):
    return PhaseRuleAccount(
        tuple(HeldLabel("chemical-component", f"c{i}") for i in range(1, components + 1)),
        tuple(HeldLabel("chemical-phase", f"p{i}") for i in range(1, phases + 1)),
        (HeldLabel("phase-environment-coordinate", "temperature"), HeldLabel("phase-environment-coordinate", "pressure")),
    )


def test_phase_cancellation_yields_two_one_and_EmptyOne():
    assert independent_degree_support(account(1, 1)).count.value == 2
    assert independent_degree_support(account(1, 2)).count.value == 1
    assert isinstance(independent_degree_support(account(1, 3)).count, EmptyOne)


def test_excess_phase_support_halts_without_signed_or_zero_count():
    with pytest.raises(InadmissibleExactValue):
        independent_degree_support(account(1, 4))


def test_joint_component_phase_successor_preserves_support():
    assert joint_component_phase_successor_preserves_degree_support(account(2, 2))
    assert joint_component_phase_successor_preserves_degree_support(account(1, 3))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(PHASE_RULE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(PHASE_RULE_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_18_rows_and_no_degree_outcomes():
    rows = _identities(ROOT)
    forbidden = {"degree_support_external_inscription", "sft_degree_support_state", "external_relation_record", "target_payload_hash"}
    assert len(rows) == 18
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_value_free_and_uses_EmptyOne():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "F = C" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")}
    )
    prediction = _prediction_map(execution.output)
    assert len(prediction) == 18
    assert sum(isinstance(word.cells[5], EmptyOne) for word in prediction.values()) == 4


def test_complete_authoritative_vector_retains_all_rows_and_sources():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-011-phase-rule-v2/phase-rule-primary-records-v1.json").read_text())
    analysis = exact_phase_rule_analysis(_source_rows(ROOT), primary)
    assert analysis["all_18_component_phase_rows_retained"]
    assert analysis["all_14_positive_degree_supports_retained"]
    assert analysis["all_four_external_zero_glyphs_translated_only_to_EmptyOne"]
    assert analysis["complete_iupac_source_retained"]
    assert analysis["complete_32_page_nist_source_retained"]
    assert analysis["no_subtraction_signed_count_or_numerical_zero_imported"]


def test_postseal_validator_preserves_structure_rows_and_controls():
    result = PhaseRuleValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 27
