from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.rotational_constant_law_v1 import (
    EXACT_RESULT,
    RotationalAxisCarrier,
    adjacent_rotational_gap_multiple,
    exact_axis_rotational_constant,
    repeated_equal_interval_constant,
    rotational_level_multiple,
    rotational_level_ratio,
    unexcited_rotational_form,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rotational_constant_batch_v1 import ROTATIONAL_CONSTANT_SPEC
from sft.chemistry.rotational_constant_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_exact_axis_ratio_and_equal_interval_successor() -> None:
    constant = exact_axis_rotational_constant(PositiveCount(12), PositiveCount(3))
    repeated = repeated_equal_interval_constant(PositiveCount(12), PositiveCount(3), PositiveCount(5))
    assert constant.fraction == Fraction(4, 1)
    assert repeated.fraction == constant.fraction


def test_positive_rotational_ladder_and_gap() -> None:
    assert tuple(rotational_level_multiple(PositiveCount(j)).value for j in range(1, 5)) == (2, 6, 12, 20)
    assert tuple(adjacent_rotational_gap_multiple(PositiveCount(j)).value for j in range(1, 5)) == (2, 4, 6, 8)
    assert rotational_level_ratio(
        exact_axis_rotational_constant(PositiveCount(12), PositiveCount(3)), PositiveCount(3)
    ).fraction == Fraction(48, 1)
    assert isinstance(unexcited_rotational_form(), EmptyOne)


def test_invalid_or_erased_count_halts() -> None:
    with pytest.raises(InadmissibleExactValue):
        exact_axis_rotational_constant(PositiveCount(1), None)
    with pytest.raises(InadmissibleExactValue):
        repeated_equal_interval_constant(PositiveCount(1), PositiveCount(1), None)
    with pytest.raises(InadmissibleExactValue):
        rotational_level_multiple(None)


def test_complete_axis_carrier_preserves_geometry_and_axis() -> None:
    carrier = RotationalAxisCarrier(
        HeldLabel("molecular-species", "witness-species"),
        HeldLabel("molecular-state", "witness-state"),
        HeldLabel("generated-molecular-geometry", "finite-coordinate-word"),
        PositiveCount(3),
        HeldLabel("rotational-axis", "principal-axis-B"),
        HeldLabel("rotational-axis-equivalence", "B-C-equivalent"),
        PositiveCount(9),
        PositiveCount(3),
        HeldLabel("observation-interval-unit", "centimeter"),
    )
    assert carrier.exact_constant.fraction == Fraction(3, 1)
    with pytest.raises(InadmissibleExactValue):
        RotationalAxisCarrier(
            carrier.species, carrier.molecular_state, carrier.geometry, carrier.geometry_coordinate_count,
            HeldLabel("rotational-axis", "merged-axis"), carrier.axis_equivalence_class,
            carrier.recurrence_count, carrier.observation_interval_count, carrier.interval_unit,
        )


def test_registered_survivor_contains_no_imported_inertia_or_continuum_form() -> None:
    assert "exact-axis-recurrence-over-interval-ratio" in EXACT_RESULT
    assert "positive-JJplusOne-level-and-2J-gap" in EXACT_RESULT
    assert "inertia" not in EXACT_RESULT
    assert "continuum" not in EXACT_RESULT


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(ROTATIONAL_CONSTANT_SPEC, "sha256:" + "a" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(ROTATIONAL_CONSTANT_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_rotational_target() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/rotational_constant_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {
        "measurement_present", "rotational_constant_inscription_cm_inverse",
        "exact_positive_axis_recurrence_ratio_per_centimeter", "external_measurement_absence",
    }
    assert document["all_rotational_constant_values_absent"] is True
    assert document["complete_displayed_molecular_row_count"] == 1005
    assert len(document["rows"]) == 3015
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    assert not any(instruction["opcode"] == "ratio" for instruction in document["instructions"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 3015


def test_complete_nist_rotational_vector_reconstructs_exactly() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == 3015
    assert len({row["target_id"] for row in rows}) == 3015
    assert len({row["displayed_molecular_row"] for row in rows}) == 1005
    assert sum(row["measurement_present"] for row in rows) == 1681
    assert sum(not row["measurement_present"] for row in rows) == 1334
    assert all(isinstance(row["vault_value"], PositiveRatio) and row["vault_value"].fraction > 0 for row in rows if row["measurement_present"])
    assert all(isinstance(row["vault_value"], EmptyOne) for row in rows if not row["measurement_present"])


def test_complete_list_choice_result_boundary_is_preserved() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/rotational-constant-primary-records-v1.json").read_text(encoding="utf-8")
    )
    assert document["complete_listed_species_count"] == 2186
    assert document["complete_unique_formula_composition_query_count"] == 1193
    assert document["complete_returned_charge_state_choice_count"] == 1832
    assert document["complete_listed_composition_without_returned_choice_count"] == 83
    assert document["complete_displayed_molecular_row_count"] == 1005
    assert document["complete_displayed_axis_cell_count"] == 3015
    assert len(document["retrieval_batches"]) == 6
