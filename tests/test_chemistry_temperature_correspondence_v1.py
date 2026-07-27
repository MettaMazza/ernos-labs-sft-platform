import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.temperature_correspondence_batch_v1 import TEMPERATURE_CORRESPONDENCE_SPEC
from sft.chemistry.temperature_correspondence_law_v1 import (
    EXACT_RESULT, ChemicalTemperatureContext, append_composition_preserves_common_carrier,
    attach_composition_consequence, common_thermal_equilibrium_carrier,
    consume_physics_temperature_carrier,
)
from sft.chemistry.temperature_correspondence_validation_v1 import (
    TemperatureCorrespondenceValidator, _prediction_map, _source_rows,
    exact_temperature_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def context(composition: str, route: str, carrier: PositiveRatio) -> ChemicalTemperatureContext:
    return ChemicalTemperatureContext(
        HeldLabel("chemical-composition", composition), HeldLabel("phase-identity", "held-phase"),
        HeldLabel("thermal-equilibrium-reference", "common-reference"),
        HeldLabel("thermometric-route", route), carrier,
    )


def test_chemistry_consumes_physics_carrier_unchanged() -> None:
    carrier = PositiveRatio.from_pair(5, 3)
    argon = context("argon", "acoustic", carrier)
    assert consume_physics_temperature_carrier(argon) is carrier
    consequence = attach_composition_consequence(
        argon, HeldLabel("composition-dependent-temperature-consequence", "argon-state-order"),
    )
    assert consequence.composition == argon.composition
    assert consequence.physics_temperature_carrier == carrier


def test_equilibrated_routes_share_one_carrier_and_rescaling_halts() -> None:
    carrier = PositiveRatio.from_pair(5, 3)
    acoustic = context("argon", "acoustic", carrier)
    electronic = context("resistor", "Johnson-noise", carrier)
    assert common_thermal_equilibrium_carrier(acoustic, electronic) == carrier
    with pytest.raises(InadmissibleExactValue):
        common_thermal_equilibrium_carrier(acoustic, context("tampered", "route", PositiveRatio.from_pair(7, 4)))


def test_append_only_composition_preserves_common_carrier() -> None:
    carrier = PositiveRatio.from_pair(5, 3)
    first = context("argon", "acoustic", carrier)
    second = context("resistor", "Johnson-noise", carrier)
    third = context("water", "contact", carrier)
    assert append_composition_preserves_common_carrier((first, second), third)
    with pytest.raises(InadmissibleExactValue):
        append_composition_preserves_common_carrier((first, second), context("tampered", "contact", PositiveRatio.from_pair(7, 4)))


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(TEMPERATURE_CORRESPONDENCE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(TEMPERATURE_CORRESPONDENCE_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/chemical_temperature_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = {
        "exact_si_common_carrier_scaled_numerator", "common_scale_denominator",
        "measured_center_scaled_numerator", "measured_standard_uncertainty_scaled_numerator",
        "measured_interval_lower_scaled_numerator", "measured_interval_upper_scaled_numerator",
        "temperature_measures_average_kinetic_energy", "noise_power_depends_on_resistance_and_temperature",
    }
    assert document["all_values_uncertainties_intervals_and_relation_flags_absent"] is True
    assert len(document["rows"]) == 3
    assert all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "measured_center_scaled_numerator" not in rendered
    assert "measured_interval_lower_scaled_numerator" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 3


def test_complete_external_value_vector_matches_exact_common_carrier() -> None:
    rows = _source_rows(ROOT)
    analysis = exact_temperature_analysis(rows)
    assert analysis["exact_common_carrier_scaled_numerator"] == 13806490
    assert analysis["common_scale_denominator"] == 10**30
    assert analysis["acoustic_interval"] == (13806456, 13806512)
    assert analysis["electronic_interval"] == (13806340, 13806680)
    assert all(bool(value) for key, value in analysis.items() if key not in {"exact_common_carrier_scaled_numerator", "common_scale_denominator", "acoustic_interval", "electronic_interval"})


def test_postseal_validator_preserves_all_values_and_controls() -> None:
    result = TemperatureCorrespondenceValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 10
