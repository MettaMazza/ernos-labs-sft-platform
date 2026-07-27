import json
from pathlib import Path
from types import SimpleNamespace

from sft.chemistry.enthalpy_equivalent_state_batch_v1 import ENTHALPY_EQUIVALENT_STATE_SPEC
from sft.chemistry.enthalpy_equivalent_state_law_v1 import (
    EnvironmentTransferPart, append_environment_part_preserves_state, compose_enthalpy_equivalent_content,
    enthalpy_equivalent_state, exact_enthalpy_state_relation,
)
from sft.chemistry.enthalpy_equivalent_state_validation_v1 import (
    EnthalpyEquivalentStateValidator, _prediction_map, exact_enthalpy_analysis, prediction_program_document,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.internal_energy_composition_validation_v1 import VALUE_COLUMNS, _source_rows
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel
from sft.physics.generated_empirical_law import survivor_id


ROOT=Path(__file__).resolve().parents[1]


def parts():
    return (EnvironmentTransferPart(HeldLabel("environment-transfer-part","first"),PositiveRatio.from_pair(2,3)),EnvironmentTransferPart(HeldLabel("environment-transfer-part","second"),PositiveRatio.from_pair(5,4)))


def state(label,internal,environment_parts):
    return enthalpy_equivalent_state(HeldLabel("chemical-composition","water"),HeldLabel("molecular-state",label),HeldLabel("phase-identity","held"),HeldLabel("held-environment","one-bar"),PositiveRatio.from_pair(internal,3),environment_parts)


def test_EmptyOne_environment_preserves_internal_content():
    base=state("base",5,EmptyOne()); assert base.enthalpy_equivalent_content==base.internal_energy


def test_exact_internal_and_environment_composition():
    assert compose_enthalpy_equivalent_content(PositiveRatio.from_pair(5,3),parts())==PositiveRatio.from_pair(43,12)


def test_orientation_is_held_and_equality_structural():
    first=state("first",5,parts()); second=state("second",8,parts())
    assert exact_enthalpy_state_relation(first,second).orientation.label=="enthalpy-rise"
    assert isinstance(exact_enthalpy_state_relation(first,first).exact_positive_magnitude,EmptyOne)


def test_append_only_environment_successor():
    extension=EnvironmentTransferPart(HeldLabel("environment-transfer-part","third"),PositiveRatio.from_pair(7,5))
    assert append_environment_part_preserves_state(PositiveRatio.from_pair(5,3),parts(),extension)


def test_candidate_grammar_complete_unique_depth_independent():
    program=GeneratedObservationalChemistryProgram(ENTHALPY_EQUIVALENT_STATE_SPEC,"sha256:"+"d"*64); candidates=program.generate_candidates().candidates; decisions=tuple(program.decide_candidate(c) for c in candidates); closure=program.closure_evidence(decisions)
    assert len(candidates)==len({c.candidate_id for c in candidates})==256; assert sum(d.survives for d in decisions)==1
    assert next(d.candidate_id for d in decisions if d.survives)==survivor_id(ENTHALPY_EQUIVALENT_STATE_SPEC); assert closure.scope.value=="depth_independent"


def test_identity_registry_value_free_for_enthalpy():
    document=json.loads((ROOT/"experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json").read_text()); forbidden=set(VALUE_COLUMNS)|{"snapshot_hash","target_payload","target_payload_hash"}
    assert len(document["rows"])==13 and all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_has_no_enthalpy_or_component_values():
    document=prediction_program_document(ROOT); rendered=json.dumps(document,sort_keys=True)
    for forbidden in ("enthalpy-kilojoule-per-mole","internal-energy-kilojoule-per-mole","volume-litre-per-mole","pressure-bar"): assert forbidden not in rendered
    execution=CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document),{"registered-premise":HeldLabel("sealed-derivation","unit-check")}); assert len(_prediction_map(execution.output))==13


def test_complete_external_enthalpy_vector_and_validator():
    analysis=exact_enthalpy_analysis(_source_rows(ROOT)); assert len(analysis["enthalpy_values_kilojoule_per_mole"])==13; assert len(analysis["adjacent_exact_positive_enthalpy_steps"])==12; assert all(bool(v) for k,v in analysis.items() if not isinstance(v,tuple))
    result=EnthalpyEquivalentStateValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:"+"a"*64)); assert result.passed is True and result.all_rows_preserved is True and len(result.measurements)==22
