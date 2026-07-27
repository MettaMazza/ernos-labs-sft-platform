import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.finite_microstate_batch_v1 import FINITE_MICROSTATE_SPEC
from sft.chemistry.finite_microstate_law_v1 import (
    EXACT_RESULT, ChemicalMicrostate, FiniteChemicalSupport, MacroObservationFibre,
    append_generated_microstate, exact_statistical_weight, finite_multiplicity,
    finite_successor_preserves_prior_assignments,
)
from sft.chemistry.finite_microstate_validation_v1 import (
    FiniteMicrostateValidator, _prediction_map, _source_rows, prediction_program_document,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def state(label: str) -> ChemicalMicrostate:
    return ChemicalMicrostate(
        HeldLabel("chemical-microstate", label), HeldLabel("chemical-composition", "water"),
        HeldLabel("phase-identity", "gas"), HeldLabel("observation-condition", "held"),
        HeldLabel("internal-state-identity", label + "-state"),
    )


def support() -> FiniteChemicalSupport:
    first, second, third = state("first"), state("second"), state("third")
    return FiniteChemicalSupport(
        (first, second, third),
        (
            MacroObservationFibre(HeldLabel("chemical-macrostate", "first-class"), (first, second)),
            MacroObservationFibre(HeldLabel("chemical-macrostate", "second-class"), (third,)),
        ),
    )


def test_complete_partition_forces_exact_multiplicity_and_weight() -> None:
    complete = support()
    first, second = complete.fibres
    assert finite_multiplicity(first) == PositiveCount(2)
    assert exact_statistical_weight(complete, first.macrostate_id) == PositiveRatio.from_pair(2, 3)
    assert exact_statistical_weight(complete, second.macrostate_id) == PositiveRatio.from_pair(1, 3)


def test_overlap_omission_duplicate_and_unknown_macrostate_halt() -> None:
    first, second, third = state("first"), state("second"), state("third")
    with pytest.raises(InadmissibleExactValue):
        FiniteChemicalSupport(
            (first, second, third),
            (
                MacroObservationFibre(HeldLabel("chemical-macrostate", "a"), (first, second)),
                MacroObservationFibre(HeldLabel("chemical-macrostate", "b"), (second, third)),
            ),
        )
    with pytest.raises(InadmissibleExactValue):
        FiniteChemicalSupport(
            (first, second, third),
            (MacroObservationFibre(HeldLabel("chemical-macrostate", "a"), (first, second)),),
        )
    with pytest.raises(InadmissibleExactValue):
        exact_statistical_weight(support(), HeldLabel("chemical-macrostate", "unknown"))


def test_finite_successor_preserves_all_prior_assignments() -> None:
    complete = support()
    fourth = state("fourth")
    new_macrostate = HeldLabel("chemical-macrostate", "successor")
    assert finite_successor_preserves_prior_assignments(complete, fourth, new_macrostate)
    extended = append_generated_microstate(complete, fourth, new_macrostate)
    assert extended.microstates[:-1] == complete.microstates
    assert extended.fibres[:-1] == complete.fibres
    with pytest.raises(InadmissibleExactValue):
        append_generated_microstate(complete, complete.microstates[0], new_macrostate)


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(FINITE_MICROSTATE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(FINITE_MICROSTATE_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/finite_microstate_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = {
        "cells", "temperature_inscription_kelvin", "heat_capacity_inscription", "entropy_inscription",
        "held_gibbs_reference_relation_inscription", "enthalpy_reference_relation_inscription",
        "target_payload", "target_payload_hash", "population", "measured_value",
    }
    assert document["all_populations_temperatures_and_calorimetric_values_absent"] is True
    assert len(document["rows"]) == 387
    assert all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "temperature_inscription_kelvin" not in rendered
    assert "heat_capacity_inscription" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 387


def test_complete_external_structure_surface_and_regime_boundary() -> None:
    rows = _source_rows(ROOT)
    population = tuple(row for row in rows if row["source_class"].startswith("direct-"))
    calorimetric = tuple(row for row in rows if row["source_class"].startswith("evaluated-"))
    assert len(rows) == len({row["target_id"] for row in rows}) == 387
    assert len(population) == 330 and len(calorimetric) == 57
    assert sum(row["target_payload"].get("temperature_inscription_kelvin") == "1700." for row in calorimetric) == 2


def test_postseal_validator_preserves_every_row_and_control() -> None:
    result = FiniteMicrostateValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 395
