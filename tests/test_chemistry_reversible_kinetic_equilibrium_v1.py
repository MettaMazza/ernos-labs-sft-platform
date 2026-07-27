from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.reversible_kinetic_equilibrium_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.reversible_kinetic_equilibrium_law_v1 import (
    CompleteReversibleFamily, CompleteReversiblePairGraph, RegisteredReversiblePair, RetainedDirectedTransition,
    append_reversible_pair_preserves_complete_family, forced_reversible_kinetic_equilibrium_correspondence,
)
from sft.chemistry.reversible_kinetic_equilibrium_validation_v1 import (
    _identities, _source_rows, exact_reversible_kinetic_equilibrium_analysis, prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def transition(label: str, entry: str, exit: str, orientation: str, condition: str = "held") -> RetainedDirectedTransition:
    return RetainedDirectedTransition(
        HeldLabel("registered-reversible-transition", label),
        HeldLabel("registered-reversible-state", entry), HeldLabel("registered-reversible-state", exit),
        HeldLabel("held-transition-orientation", orientation), HeldLabel("held-reversible-condition", condition),
        HeldLabel("held-reversible-status", "measured"),
    )


def graph(label: str, first: str, second: str) -> CompleteReversiblePairGraph:
    return CompleteReversiblePairGraph(
        HeldLabel("registered-reversible-pair", label),
        HeldLabel("registered-reversible-state", first), HeldLabel("registered-reversible-state", second),
        transition(label + "-forward", first, second, "first-to-second"),
        transition(label + "-reverse", second, first, "second-to-first"),
    )


def test_same_graph_forces_kinetic_word_and_equilibrium_support():
    pair = graph("pair-ab", "a", "b")
    result = forced_reversible_kinetic_equilibrium_correspondence(pair)
    assert result.graph_edge_count.value == 2
    assert result.recurrence_support == (pair.first_state, pair.second_state)
    assert result.directed_transition_word == (pair.forward_transition, pair.reverse_transition)


def test_reversible_pair_successor_preserves_every_prior_correspondence():
    family = CompleteReversibleFamily((RegisteredReversiblePair(PositiveCount(1), graph("pair-ab", "a", "b")),))
    assert append_reversible_pair_preserves_complete_family(
        family, RegisteredReversiblePair(PositiveCount(2), graph("pair-cd", "c", "d"))
    )


def test_broken_reverse_boundary_and_mismatched_condition_are_rejected():
    with pytest.raises(InadmissibleExactValue):
        CompleteReversiblePairGraph(
            HeldLabel("registered-reversible-pair", "broken"),
            HeldLabel("registered-reversible-state", "a"), HeldLabel("registered-reversible-state", "b"),
            transition("a-b", "a", "b", "forward"), transition("c-a", "c", "a", "reverse"),
        )
    with pytest.raises(InadmissibleExactValue):
        CompleteReversiblePairGraph(
            HeldLabel("registered-reversible-pair", "conditions"),
            HeldLabel("registered-reversible-state", "a"), HeldLabel("registered-reversible-state", "b"),
            transition("a-b", "a", "b", "forward", "one"), transition("b-a", "b", "a", "reverse", "two"),
        )


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC) for row in rows) == 1


def test_value_free_164_identity_registry_precedes_complete_target_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 164
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert all("target_payload" not in row and "target_payload_hash" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_both_directions_disagreements_and_all_sources():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_reversible_kinetic_equilibrium_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["same_exact_pair_graph_supplies_both_directions"]
    assert analysis["exact_forward_direction_retained"] and analysis["exact_reverse_direction_retained"]
    assert analysis["forward_reverse_terminal_disagreement_retained_without_average"]
    assert analysis["source_direction_label_disagreements_retained"]
    assert analysis["complete_source_class_census_matches"]
    assert analysis["complete_movie_retained"] and analysis["all_archive_members_retained"]


def test_omitted_complete_source_record_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_reversible_kinetic_equilibrium_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    execution_path = ROOT / "claims/SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009/execution.py"
    definition = importlib.util.spec_from_file_location("kin009_execution", execution_path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
