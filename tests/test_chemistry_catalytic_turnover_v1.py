from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.catalytic_turnover_batch_v1 import (
    CATALYTIC_TURNOVER_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.catalytic_turnover_law_v1 import (
    CompleteCatalyticCycle, CompleteCatalyticCycleFamily, RegisteredCatalyticCycleOccurrence,
    RetainedCatalystState, RetainedCatalyticTransition, append_complete_cycle_preserves_turnover_family,
    forced_catalytic_turnover, forced_cycle_frequency,
)
from sft.chemistry.catalytic_turnover_validation_v1 import (
    _identities, _source_rows, exact_catalytic_turnover_analysis, prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def cycle(label: str = "cycle-a", catalyst_label: str = "catalyst-a") -> CompleteCatalyticCycle:
    catalyst = HeldLabel("held-catalyst-identity", catalyst_label)
    states = tuple(
        RetainedCatalystState(
            HeldLabel("registered-catalytic-state", f"{label}-state-{position}"), catalyst,
            PositiveCount(position), HeldLabel("held-catalytic-state-status", "retained"),
        )
        for position in range(1, 6)
    )
    transitions = tuple(
        RetainedCatalyticTransition(
            HeldLabel("registered-catalytic-transition", f"edge-{position + 1}"),
            states[position].state_identity, states[(position + 1) % len(states)].state_identity,
            HeldLabel("held-catalytic-process", f"process-{position + 1}"),
            HeldLabel("held-catalytic-condition", "held"), HeldLabel("held-catalytic-transition-status", "retained"),
        )
        for position in range(len(states))
    )
    return CompleteCatalyticCycle(HeldLabel("registered-catalytic-cycle", label), states, transitions)


def test_complete_return_word_forces_one_turnover_and_exact_frequency():
    complete = cycle()
    turnover = forced_catalytic_turnover(complete)
    frequency = forced_cycle_frequency(PositiveCount(7), PositiveCount(5))
    assert turnover.completed_cycle_count.value == 1
    assert turnover.exact_return_state == complete.ordered_states[0].state_identity
    assert turnover.ordered_transition_word[-1].exit_state == turnover.exact_return_state
    assert (frequency.cycle_frequency.value.numerator, frequency.cycle_frequency.value.denominator) == (7, 5)


def test_complete_cycle_successor_preserves_every_prior_turnover():
    family = CompleteCatalyticCycleFamily((
        RegisteredCatalyticCycleOccurrence(PositiveCount(1), cycle("cycle-a", "catalyst-a"), PositiveCount(7)),
    ))
    assert append_complete_cycle_preserves_turnover_family(
        family, RegisteredCatalyticCycleOccurrence(PositiveCount(2), cycle("cycle-b", "catalyst-b"), PositiveCount(5)),
    )


def test_broken_return_and_changed_catalyst_identity_are_rejected():
    complete = cycle()
    broken_edges = complete.ordered_transitions[:-1] + (
        RetainedCatalyticTransition(
            HeldLabel("registered-catalytic-transition", "broken"), complete.ordered_states[-1].state_identity,
            HeldLabel("registered-catalytic-state", "not-entry"), HeldLabel("held-catalytic-process", "broken"),
            HeldLabel("held-catalytic-condition", "held"), HeldLabel("held-catalytic-transition-status", "tampered"),
        ),
    )
    with pytest.raises(InadmissibleExactValue):
        CompleteCatalyticCycle(complete.cycle_identity, complete.ordered_states, broken_edges)
    changed_states = complete.ordered_states[:-1] + (
        RetainedCatalystState(
            complete.ordered_states[-1].state_identity, HeldLabel("held-catalyst-identity", "substituted"),
            complete.ordered_states[-1].cycle_position, complete.ordered_states[-1].observation_status,
        ),
    )
    with pytest.raises(InadmissibleExactValue):
        CompleteCatalyticCycle(complete.cycle_identity, changed_states, complete.ordered_transitions)


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(CATALYTIC_TURNOVER_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(CATALYTIC_TURNOVER_SPEC) for row in rows) == 1


def test_value_free_497_identity_registry_precedes_complete_target_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 497
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert all("target_payload" not in row and "target_payload_hash" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_cycle_values_raw_rows_and_adverse_evidence():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_catalytic_turnover_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["same_catalyst_identity_retained_through_all_five_states"]
    assert analysis["final_transition_returns_exact_entry_state"]
    assert analysis["five_structural_states_and_four_observed_levels_distinguished"]
    assert analysis["complete_seven_row_turnover_vector_retained"]
    assert analysis["independent_rate_tables_retained_separately_without_average"]
    assert analysis["complete_385617_raw_trace_rows_retained"]
    assert analysis["complete_1604_frame_movie_retained"] and analysis["all_387_archive_members_retained"]
    assert analysis["unavailable_article_pdf_adverse_record_retained"]
    assert analysis["low_temperature_insufficient_fit_adverse_record_retained"]


def test_omitted_complete_source_record_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_catalytic_turnover_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    execution_path = ROOT / "claims/SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010/execution.py"
    definition = importlib.util.spec_from_file_location("kin010_execution", execution_path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == CATALYTIC_TURNOVER_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
