from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.vibrational_frequency_batch_v1 import VIBRATIONAL_FREQUENCY_SPEC
from sft.chemistry.vibrational_frequency_law_v1 import (
    EXACT_RESULT,
    exact_recurrence_frequency,
    repeated_equal_interval_frequency,
)
from sft.chemistry.vibrational_frequency_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_exact_finite_recurrence_ratio_and_equal_interval_successor() -> None:
    frequency = exact_recurrence_frequency(PositiveCount(12), PositiveCount(3))
    repeated = repeated_equal_interval_frequency(PositiveCount(12), PositiveCount(3), PositiveCount(5))
    assert frequency.fraction == Fraction(4, 1)
    assert repeated.fraction == frequency.fraction


def test_non_count_frequency_input_halts() -> None:
    with pytest.raises(InadmissibleExactValue):
        exact_recurrence_frequency(PositiveCount(1), None)
    with pytest.raises(InadmissibleExactValue):
        repeated_equal_interval_frequency(PositiveCount(1), PositiveCount(1), None)


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(
        VIBRATIONAL_FREQUENCY_SPEC, "sha256:" + "9" * 64
    )
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(VIBRATIONAL_FREQUENCY_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_frequency_target() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/vibrational_frequency_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {
        "measurement_present", "frequency_inscription_cm_inverse",
        "exact_positive_recurrence_ratio_per_centimeter", "external_measurement_absence",
    }
    assert document["all_frequency_values_absent"] is True
    assert document["complete_displayed_molecule_count"] == 145
    assert len(document["rows"]) == 2009
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_relation_only_and_complete() -> None:
    document = prediction_program_document(ROOT)
    assert not any(instruction["opcode"] == "ratio" for instruction in document["instructions"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 2009


def test_complete_displayed_nist_vector_reconstructs_exactly() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == 2009
    assert len({row["target_id"] for row in rows}) == 2009
    assert tuple(row["vibration_count"] for row in rows) == tuple(range(1, 2010))
    assert len({row["molecule_count"] for row in rows}) == 145
    assert sum(row["measurement_present"] for row in rows) == 1984
    assert sum(not row["measurement_present"] for row in rows) == 25
    assert all(isinstance(row["vault_value"], PositiveRatio) and row["vault_value"].fraction > 0 for row in rows if row["measurement_present"])
    assert all(isinstance(row["vault_value"], EmptyOne) for row in rows if not row["measurement_present"])


def test_source_advertised_and_displayed_counts_are_both_preserved() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1/vibrational-frequency-primary-records-v1.json").read_text(encoding="utf-8")
    )
    assert document["source_advertised_molecule_count"] == 164
    assert document["source_advertised_vibration_count"] == 2452
    assert document["complete_displayed_molecule_count"] == 145
    assert document["complete_displayed_vibration_count"] == 2009
    assert document["source_advertised_but_undisplayed_molecule_count"] == 19
    assert document["source_advertised_but_undisplayed_vibration_count"] == 443
    assert document["calculated_frequency_ratio_and_fitted_scale_columns_excluded_from_derivation_and_measurement_vector"] is True
