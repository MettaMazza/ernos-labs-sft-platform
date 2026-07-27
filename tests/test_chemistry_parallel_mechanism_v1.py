from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.parallel_mechanism_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PARALLEL_MECHANISM_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH, WORKBOOK_HASH, WORKBOOK_PATH,
)
from sft.chemistry.parallel_mechanism_law_v1 import (
    CompleteParallelMechanism, RetainedParallelPath, append_parallel_path_preserves_complete_family,
    forced_parallel_mechanism_composition,
)
from sft.chemistry.parallel_mechanism_validation_v1 import (
    _identities, _source_rows, exact_parallel_mechanism_analysis, prediction_program_document,
)
from sft.chemistry.sequential_mechanism_law_v1 import (
    CompleteSequentialMechanism, RetainedElementaryTransition, RetainedMechanismState,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def state(label: str, occurrence: int) -> RetainedMechanismState:
    return RetainedMechanismState(
        HeldLabel("registered-mechanism-state", label), PositiveCount(occurrence),
        HeldLabel("held-state-condition", "held"), HeldLabel("held-observation-status", "held"),
    )


def path(label: str, row: int, labels: tuple[str, ...]) -> RetainedParallelPath:
    reaction = HeldLabel("registered-reaction", "test-reaction")
    states = tuple(state(value, ordinal) for ordinal, value in enumerate(labels, start=1))
    edges = tuple(
        RetainedElementaryTransition(
            HeldLabel("registered-elementary-transition", f"{label}-{ordinal}"), PositiveCount(ordinal),
            states[ordinal - 1].state_identity, states[ordinal].state_identity,
            HeldLabel("held-transition-condition", "held"), HeldLabel("held-transition-status", "held"),
        )
        for ordinal in range(1, len(states))
    )
    return RetainedParallelPath(
        HeldLabel("registered-parallel-path", label), PositiveCount(row),
        CompleteSequentialMechanism(reaction, states, edges), HeldLabel("held-path-status", "held"),
    )


def complete() -> CompleteParallelMechanism:
    return CompleteParallelMechanism(
        HeldLabel("registered-reaction", "test-reaction"), HeldLabel("registered-mechanism-state", "a"),
        (path("p1", 1, ("a", "b", "d")), path("p2", 2, ("a", "c", "d"))),
    )


def test_complete_parallel_family_is_exact_and_source_ordered():
    result = forced_parallel_mechanism_composition(complete())
    assert result.path_count.value == 2
    assert tuple(row.path_identity.label for row in result.ordered_paths) == ("p1", "p2")
    assert tuple(row.label for row in result.terminal_state_word) == ("d", "d")


def test_parallel_successor_preserves_every_prior_path_and_terminal_occurrence():
    assert append_parallel_path_preserves_complete_family(complete(), path("p3", 3, ("a", "e", "f", "d")))


def test_broken_common_initial_boundary_and_duplicate_path_are_rejected():
    with pytest.raises(InadmissibleExactValue):
        CompleteParallelMechanism(
            HeldLabel("registered-reaction", "test-reaction"), HeldLabel("registered-mechanism-state", "a"),
            (path("p1", 1, ("a", "b")), path("p2", 2, ("x", "c"))),
        )
    with pytest.raises(InadmissibleExactValue):
        CompleteParallelMechanism(
            HeldLabel("registered-reaction", "test-reaction"), HeldLabel("registered-mechanism-state", "a"),
            (path("p1", 1, ("a", "b")), path("p1", 2, ("a", "c"))),
        )


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(PARALLEL_MECHANISM_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(PARALLEL_MECHANISM_SPEC) for row in rows) == 1


def test_value_free_identity_registry_precedes_complete_withheld_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 28
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / WORKBOOK_PATH) == WORKBOOK_HASH
    assert all("target_payload" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_all_paths_sheets_cells_and_absence_glyphs():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_parallel_mechanism_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["three_complete_paths_retained"]
    assert analysis["all_seven_product_identities_covered_without_selection"]
    assert analysis["complete_registered_rectangular_cell_position_count"] == 18158
    assert analysis["complete_cell_class_census"] == {
        "EmptyOne": 8968, "external_zero": 2109, "positive": 6060,
        "signed": 0, "formula": 722, "label": 299,
    }
    assert analysis["unresolved_two-structure_peak_retained_without_selection"]


def test_omitted_source_worksheet_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_parallel_mechanism_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    execution_path = ROOT / "claims/SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008/execution.py"
    definition = importlib.util.spec_from_file_location("kin008_execution", execution_path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == PARALLEL_MECHANISM_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
