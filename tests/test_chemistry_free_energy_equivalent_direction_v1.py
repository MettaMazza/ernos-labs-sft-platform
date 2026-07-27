import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from sft.chemistry.free_energy_equivalent_direction_batch_v1 import FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC
from sft.chemistry.free_energy_equivalent_direction_law_v1 import ReactionPathAccount,common_successor_preserves_direction,free_energy_equivalent_direction
from sft.chemistry.free_energy_equivalent_direction_validation_v1 import FreeEnergyEquivalentDirectionValidator,_identities,_prediction_map,_source_rows,exact_reaction_direction_analysis,prediction_program_document
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter,EmptyOne,PositiveRatio,fold_program_from_mapping
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import survivor_id
ROOT=Path(__file__).resolve().parents[1]
def account(path,energy,distinctions):return ReactionPathAccount(HeldLabel("reaction-path",path),HeldLabel("reaction-boundary","held"),HeldLabel("reaction-condition","held"),PositiveRatio.from_pair(energy,3),PositiveCount(distinctions))
def test_strict_product_order_forces_direction_and_positive_separations():
    result=free_energy_equivalent_direction(account("forward-path",5,2),account("reverse-path",8,3));assert result.orientation.label=="forward-favoured" and result.energy_separation==PositiveRatio.from_pair(1,1) and result.distinction_separation==PositiveCount(1)
def test_equal_accounts_are_structural_equilibrium():
    result=free_energy_equivalent_direction(account("forward-path",5,2),account("reverse-path",5,2));assert result.orientation.label=="equilibrium" and isinstance(result.energy_separation,EmptyOne) and isinstance(result.distinction_separation,EmptyOne)
def test_incomparable_accounts_halt_and_common_successor_preserves():
    with pytest.raises(InadmissibleExactValue):free_energy_equivalent_direction(account("forward-path",5,4),account("reverse-path",8,2))
    assert common_successor_preserves_direction(account("forward-path",5,2),account("reverse-path",8,3),PositiveRatio.from_pair(7,5),PositiveCount(2))
def test_candidate_grammar_complete_unique_depth_independent():
    program=GeneratedObservationalChemistryProgram(FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC,"sha256:"+"d"*64);candidates=program.generate_candidates().candidates;decisions=tuple(program.decide_candidate(c) for c in candidates);closure=program.closure_evidence(decisions)
    assert len(candidates)==len({c.candidate_id for c in candidates})==256 and sum(d.survives for d in decisions)==1 and next(d.candidate_id for d in decisions if d.survives)==survivor_id(FREE_ENERGY_EQUIVALENT_DIRECTION_SPEC) and closure.scope.value=="depth_independent"
def test_identity_registry_has_all_64_rows_and_no_values():
    rows=_identities(ROOT);assert len(rows)==64;forbidden={"temperature-kelvin","NO2_complete_row","N2O4_complete_row","held-reaction-direction","target_payload_hash"};assert all(not forbidden.intersection(row) for row in rows)
def test_prediction_is_complete_and_value_free():
    document=prediction_program_document(ROOT);rendered=json.dumps(document,sort_keys=True)
    for forbidden in ("temperature-kelvin","formation-gibbs-kilojoule-per-mole","log10-formation-equilibrium-constant","held-reaction-direction"):assert forbidden not in rendered
    execution=CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document),{"registered-premise":HeldLabel("sealed-derivation","unit-check")});assert len(_prediction_map(execution.output))==64
def test_complete_external_vector_retains_both_directions_and_crossing():
    analysis=exact_reaction_direction_analysis(_source_rows(ROOT));assert analysis["five_reverse_and_fifty_nine_forward_rows_retained"] and analysis["single_direction_crossing_retained"] and analysis["exact_crossing_bracket_300_to_350_kelvin"] and analysis["all_Gibbs_logK_signs_opposed"]
def test_postseal_validator_preserves_all_rows_values_and_controls():
    result=FreeEnergyEquivalentDirectionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:"+"a"*64));assert result.passed is True and result.all_rows_preserved is True and len(result.measurements)==72
