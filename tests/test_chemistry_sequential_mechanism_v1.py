from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.sequential_mechanism_batch_v1 import PRIMARY_PATH, SEQUENTIAL_MECHANISM_SPEC
from sft.chemistry.sequential_mechanism_law_v1 import (
    CompleteSequentialMechanism, RetainedElementaryTransition, RetainedMechanismState,
    append_elementary_successor_preserves_complete_prefix, forced_sequential_mechanism_composition,
)
from sft.chemistry.sequential_mechanism_validation_v1 import (
    _identities, _source_rows, exact_sequential_mechanism_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def state(label: str, ordinal: int) -> RetainedMechanismState:
    return RetainedMechanismState(
        HeldLabel("registered-mechanism-state", label), PositiveCount(ordinal),
        HeldLabel("held-state-condition", f"condition-{ordinal}"),
        HeldLabel("held-observation-status", "retained"),
    )


def edge(label: str, ordinal: int, entry: str, exit: str) -> RetainedElementaryTransition:
    return RetainedElementaryTransition(
        HeldLabel("registered-elementary-transition", label), PositiveCount(ordinal),
        HeldLabel("registered-mechanism-state", entry), HeldLabel("registered-mechanism-state", exit),
        HeldLabel("held-transition-condition", f"boundary-{ordinal}"),
        HeldLabel("held-transition-status", "retained"),
    )


def mechanism(labels: tuple[str, ...]) -> CompleteSequentialMechanism:
    return CompleteSequentialMechanism(
        HeldLabel("registered-reaction", "reaction"),
        tuple(state(label, ordinal) for ordinal, label in enumerate(labels, start=1)),
        tuple(edge(f"edge-{ordinal}", ordinal, labels[ordinal - 1], labels[ordinal]) for ordinal in range(1, len(labels))),
    )


def test_exact_composition_retains_every_state_edge_and_intermediate() -> None:
    source = mechanism(("a", "b", "c"))
    result = forced_sequential_mechanism_composition(source)
    assert result.ordered_states == source.ordered_states
    assert result.ordered_transitions == source.ordered_transitions
    assert result.intermediate_states == (source.ordered_states[1],)
    assert result.transition_count.value == 2 and result.intermediate_count.value == 1


def test_two_state_base_uses_emptyone_not_numerical_zero() -> None:
    result = forced_sequential_mechanism_composition(mechanism(("a", "b")))
    assert result.transition_count.value == 1
    assert isinstance(result.intermediate_count, EmptyOne)


def test_elementary_successor_preserves_complete_prefix() -> None:
    source = mechanism(("a", "b", "c"))
    assert append_elementary_successor_preserves_complete_prefix(
        source, state("d", 4), edge("edge-3", 3, "c", "d")
    )


def test_broken_boundary_or_non_distinguishing_edge_rejects() -> None:
    with pytest.raises(InadmissibleExactValue):
        CompleteSequentialMechanism(
            HeldLabel("registered-reaction", "reaction"), (state("a", 1), state("b", 2)),
            (edge("wrong", 1, "x", "b"),),
        )
    with pytest.raises(InadmissibleExactValue):
        edge("no-distinction", 1, "a", "a")


def test_complete_value_free_seventeen_record_identity_surface() -> None:
    rows = _identities(ROOT)
    forbidden = {"source_condition_external_inscription", "XTX_component_exact_occupancy", "measured_difference_density_features"}
    assert len(rows) == 17
    assert all(not forbidden.intersection(row) for row in rows)
    assert tuple(row["source_row"] for row in rows) == tuple(range(1, 18))


def test_complete_external_sequence_analysis_retains_adverse_and_unresolved_rows() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_sequential_mechanism_analysis(rows, primary)
    assert analysis["deposited_XTX_occupancy_vector"] == ("1", "9/10", "9/10", "17/20", "13/20")
    assert analysis["three_distinct_experimental_states_force_two_boundary-matched_edges"]
    assert analysis["all_seven_power_columns_and_four_features_retained"]
    assert analysis["external_absence_glyph_count_translated_to_EmptyOne"] == 6
    assert analysis["favorable_adverse_and_unresolved_controls_retained"]


def test_prediction_contains_identities_and_laws_not_target_values() -> None:
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert "source_condition_external_inscription" not in serialized
    assert "XTX_component_exact_occupancy" not in serialized
    assert "measured_difference_density_features" not in serialized
    assert "KIN-007-SEQUENTIAL-RECORD-01" in serialized and "KIN-007-SEQUENTIAL-RECORD-17" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path_file = ROOT / "claims/SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007/execution.py"
    definition = importlib.util.spec_from_file_location("kin007_execution_test", path_file)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == SEQUENTIAL_MECHANISM_SPEC.claim_id
