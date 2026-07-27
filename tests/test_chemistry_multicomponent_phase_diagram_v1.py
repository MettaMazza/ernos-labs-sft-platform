import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.multicomponent_phase_diagram_batch_v1 import MULTICOMPONENT_PHASE_DIAGRAM_SPEC
from sft.chemistry.multicomponent_phase_diagram_law_v1 import (
    ComponentExchangeSupport, ExactPhaseCompositionWord, FiniteMulticomponentDiagram,
    MulticomponentCoexistencePoint, PhaseCompositionCoordinate, append_coexistence_point,
    common_exchange_replication_preserves_point, multicomponent_two_phase_degree_support,
)
from sft.chemistry.multicomponent_phase_diagram_validation_v1 import (
    MulticomponentPhaseDiagramValidator, _identities, _prediction_map, _source_rows,
    exact_multicomponent_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def coordinate(label, numerator=None, denominator=None):
    value = EmptyOne() if numerator is None else PositiveRatio.from_pair(numerator, denominator)
    return PhaseCompositionCoordinate(HeldLabel("chemical-component", label), value)


def point():
    liquid_coordinates = (coordinate("a", 2, 5), coordinate("b", 3, 5))
    gas_coordinates = (coordinate("a", 3, 5), coordinate("b", 2, 5))
    exchange = tuple(ComponentExchangeSupport(row.component_identity, PositiveCount(4), PositiveCount(4)) for row in liquid_coordinates)
    return MulticomponentCoexistencePoint(
        ExactPhaseCompositionWord(HeldLabel("chemical-phase", "liquid"), liquid_coordinates),
        ExactPhaseCompositionWord(HeldLabel("chemical-phase", "gas"), gas_coordinates),
        PositiveRatio.from_pair(7, 2), PositiveRatio.from_pair(9, 4), exchange,
    )


def test_exact_phase_words_close_to_one_with_structural_absence():
    word = ExactPhaseCompositionWord(
        HeldLabel("chemical-phase", "liquid"),
        (coordinate("a"), coordinate("b", 1, 1)),
    )
    assert isinstance(word.coordinates[0].coordinate, EmptyOne)


def test_invalid_composition_or_exchange_halts():
    with pytest.raises(InadmissibleExactValue):
        ExactPhaseCompositionWord(
            HeldLabel("chemical-phase", "liquid"),
            (coordinate("a", 1, 2), coordinate("b", 1, 3)),
        )
    valid = point()
    with pytest.raises(InadmissibleExactValue):
        MulticomponentCoexistencePoint(
            valid.first_phase, valid.second_phase, valid.temperature_support, valid.pressure_support,
            tuple(ComponentExchangeSupport(row.component_identity, PositiveCount(4), PositiveCount(5)) for row in valid.first_phase.coordinates),
        )


def test_phase_rank_append_and_replication_are_exact():
    state = point()
    assert multicomponent_two_phase_degree_support(state).value == 2
    diagram = append_coexistence_point(FiniteMulticomponentDiagram((state,)), state)
    assert len(diagram.points) == 2
    assert common_exchange_replication_preserves_point(state, PositiveCount(7))


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(MULTICOMPONENT_PHASE_DIAGRAM_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MULTICOMPONENT_PHASE_DIAGRAM_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_has_116_rows_and_no_values():
    rows = _identities(ROOT)
    forbidden = {
        "component_orgnums", "temperature_K_external_inscription", "pressure_kPa_external_inscription",
        "liquid_reported_mole_fraction_external_inscription", "gas_reported_mole_fraction_external_inscription",
        "target_payload_hash",
    }
    assert len(rows) == 116
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in (
        "temperature_K_external_inscription", "pressure_kPa_external_inscription",
        "liquid_reported_mole_fraction_external_inscription", "gas_reported_mole_fraction_external_inscription",
    ):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 116


def test_complete_external_vector_retains_all_records_and_absence_boundaries():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-013-multicomponent-phase-diagram-v1/multicomponent-phase-diagram-primary-records-v1.json").read_text())
    analysis = exact_multicomponent_analysis(_source_rows(ROOT), primary)
    assert analysis["all_116_records_retained"]
    assert analysis["all_65_binary_and_51_ternary_records_retained"]
    assert analysis["all_five_binary_pairs_and_complete_ternary_surface_retained"]
    assert analysis["all_566_exact_phase_coordinates_close_to_One"]
    assert analysis["all_12_absent_coordinates_are_EmptyOne"]
    assert analysis["complete_parent_source_preserved"]
    assert analysis["no_imported_phase_geometry_eos_interpolation_or_fit"]


def test_postseal_validator_preserves_values_rows_and_controls():
    result = MulticomponentPhaseDiagramValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 128
