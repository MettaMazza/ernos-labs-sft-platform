from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.diffusion_limited_reaction_batch_v1 import (
    DIFFUSION_LIMITED_REACTION_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.diffusion_limited_reaction_law_v1 import (
    CompleteFiniteTransportPath, CompleteTransportReactionFamily, RegisteredTransportReactionOccurrence,
    RetainedReactionOccurrence, RetainedTransportState, RetainedTransportTransition,
    append_transport_reaction_preserves_complete_family, forced_diffusion_limited_reaction_boundary,
)
from sft.chemistry.diffusion_limited_reaction_validation_v1 import (
    _identities, _source_rows, exact_diffusion_limited_reaction_analysis, prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def path(label: str = "path-a", reactant_label: str = "reactant-a") -> CompleteFiniteTransportPath:
    reactant = HeldLabel("held-transported-reactant", reactant_label)
    states = tuple(
        RetainedTransportState(
            HeldLabel("registered-transport-reaction-state", f"{label}-state-{position}"), reactant,
            PositiveCount(position), HeldLabel("held-transport-state-status", "retained"),
        )
        for position in range(1, 5)
    )
    condition = HeldLabel("held-transport-reaction-condition", "held")
    transitions = tuple(
        RetainedTransportTransition(
            HeldLabel("registered-transport-transition", f"{label}-edge-{position + 1}"),
            states[position].state_identity, states[position + 1].state_identity, condition,
            HeldLabel("held-transport-transition-status", "retained"),
        )
        for position in range(len(states) - 1)
    )
    return CompleteFiniteTransportPath(HeldLabel("registered-finite-transport-path", label), states, transitions)


def reaction(transport: CompleteFiniteTransportPath, label: str = "reaction-a") -> RetainedReactionOccurrence:
    return RetainedReactionOccurrence(
        HeldLabel("registered-reaction-occurrence", label), transport.exit_state,
        HeldLabel("registered-transport-reaction-state", f"{label}-product"),
        transport.ordered_transitions[-1].condition_boundary, HeldLabel("held-reaction-status", "retained"),
    )


def test_complete_transport_word_forces_exact_reaction_boundary():
    transport = path()
    occurrence = reaction(transport)
    result = forced_diffusion_limited_reaction_boundary(transport, occurrence)
    assert result.completed_reaction_count.value == 1
    assert result.encounter_state == occurrence.encounter_entry_state
    assert len(result.complete_transport_word) == len(transport.ordered_states) - 1


def test_complete_transport_reaction_successor_preserves_every_prior_result():
    first = path("path-a", "reactant-a")
    family = CompleteTransportReactionFamily((
        RegisteredTransportReactionOccurrence(PositiveCount(1), first, reaction(first), PositiveCount(7)),
    ))
    second = path("path-b", "reactant-b")
    assert append_transport_reaction_preserves_complete_family(
        family, RegisteredTransportReactionOccurrence(PositiveCount(2), second, reaction(second, "reaction-b"), PositiveCount(5)),
    )


def test_broken_transport_word_and_reaction_entry_mismatch_are_rejected():
    transport = path()
    broken_edges = transport.ordered_transitions[:-1] + (
        RetainedTransportTransition(
            HeldLabel("registered-transport-transition", "broken"), transport.ordered_states[-2].state_identity,
            HeldLabel("registered-transport-reaction-state", "not-final-state"),
            transport.ordered_transitions[-1].condition_boundary, HeldLabel("held-transport-transition-status", "tampered"),
        ),
    )
    with pytest.raises(InadmissibleExactValue):
        CompleteFiniteTransportPath(transport.path_identity, transport.ordered_states, broken_edges)
    mismatched = RetainedReactionOccurrence(
        HeldLabel("registered-reaction-occurrence", "mismatched"),
        HeldLabel("registered-transport-reaction-state", "not-transport-exit"),
        HeldLabel("registered-transport-reaction-state", "product"),
        transport.ordered_transitions[-1].condition_boundary, HeldLabel("held-reaction-status", "tampered"),
    )
    with pytest.raises(InadmissibleExactValue):
        forced_diffusion_limited_reaction_boundary(transport, mismatched)


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(DIFFUSION_LIMITED_REACTION_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(DIFFUSION_LIMITED_REACTION_SPEC) for row in rows) == 1


def test_value_free_251_identity_registry_precedes_complete_target_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 251
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert all("target_payload" not in row and "target_payload_hash" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_paths_values_raw_rows_and_adverse_evidence():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_diffusion_limited_reaction_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["same_held_reactant_retained_through_complete_transport_word"]
    assert analysis["transport_exit_is_exact_reaction_entry"]
    assert analysis["reaction_is_admissible_only_after_complete_transport_word"]
    assert analysis["all_five_separated_solvation_transport_encounter_product_states_retained"]
    assert analysis["complete_11512_key_raw_data_rows_retained"]
    assert analysis["complete_15_row_radius_total_reaction_time_vector_retained"]
    assert analysis["complete_reaction_yield_and_coincidence_matrices_retained"]
    assert analysis["experimental_43_plus_or_minus_5_and_simulated_14_velocity_inscriptions_and_discrepancy_retained"]
    assert analysis["large_droplet_resolution_and_peer_review_adverse_records_retained"]


def test_omitted_complete_source_record_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_diffusion_limited_reaction_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    execution_path = ROOT / "claims/SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011/execution_v2.py"
    definition = importlib.util.spec_from_file_location("kin011_execution", execution_path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == DIFFUSION_LIMITED_REACTION_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
