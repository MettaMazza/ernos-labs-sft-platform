from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.reaction_dynamics_scattering_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, REACTION_DYNAMICS_SCATTERING_SPEC,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.reaction_dynamics_scattering_law_v1 import (
    CompleteFiniteProductStateSupport, CompleteScatteringFamily, RegisteredScatteringOccurrence,
    RetainedIncomingReactionChannel, RetainedOutgoingProductState,
    append_scattering_occurrence_preserves_complete_family, forced_reaction_scattering_product_state_law,
)
from sft.chemistry.reaction_dynamics_scattering_validation_v1 import (
    _identities, _source_rows, exact_reaction_dynamics_scattering_analysis, prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def incoming(reaction: str = "reaction-a") -> RetainedIncomingReactionChannel:
    return RetainedIncomingReactionChannel(
        HeldLabel("registered-incoming-reaction-channel", "incoming-a"),
        HeldLabel("held-scattering-reaction-identity", reaction),
        tuple(HeldLabel("held-incoming-channel-carrier", x) for x in ("reactant-a", "reactant-b")),
        HeldLabel("held-incoming-preparation", "preparation-a"),
    )


def outgoing(ordinal: int, orientation: str, events: int, reaction: str = "reaction-a") -> RetainedOutgoingProductState:
    return RetainedOutgoingProductState(
        PositiveCount(ordinal), HeldLabel("registered-outgoing-product-channel", f"outgoing-{ordinal}"),
        HeldLabel("held-scattering-reaction-identity", reaction),
        tuple(HeldLabel("held-outgoing-product-carrier", x) for x in ("product-a", "product-b")),
        tuple(HeldLabel("held-outgoing-product-state", x) for x in (f"state-a-{ordinal}", f"state-b-{ordinal}")),
        HeldLabel("held-incoming-outgoing-orientation", orientation), PositiveCount(events),
        HeldLabel("held-scattering-evidence-status", "retained"),
    )


def support(reaction: str = "reaction-a") -> CompleteFiniteProductStateSupport:
    return CompleteFiniteProductStateSupport(
        incoming(),
        (outgoing(1, "same-oriented", 3, reaction), outgoing(2, "transverse-oriented", 2, reaction), outgoing(3, "opposed-oriented", 1, reaction)),
    )


def test_complete_finite_channels_force_exact_state_shares_and_held_orientations():
    result = forced_reaction_scattering_product_state_law(support())
    assert tuple(row.exact_event_share for row in result) == (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    assert tuple(row.orientation_to_incoming.label for row in result) == ("same-oriented", "transverse-oriented", "opposed-oriented")


def test_scattering_successor_preserves_every_prior_result():
    first = RegisteredScatteringOccurrence(PositiveCount(1), support())
    family = CompleteScatteringFamily((first,))
    assert append_scattering_occurrence_preserves_complete_family(family, RegisteredScatteringOccurrence(PositiveCount(2), support()))


def test_mismatched_reaction_and_duplicate_outgoing_state_are_rejected():
    with pytest.raises(InadmissibleExactValue):
        support("different-reaction")
    duplicate = outgoing(1, "same-oriented", 3)
    with pytest.raises(InadmissibleExactValue):
        CompleteFiniteProductStateSupport(incoming(), (duplicate, duplicate))


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(REACTION_DYNAMICS_SCATTERING_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(REACTION_DYNAMICS_SCATTERING_SPEC) for row in rows) == 1


def test_value_free_51_identity_registry_precedes_complete_target_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 51
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert all("target_payload" not in row and "target_payload_hash" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_state_values_processing_and_adverse_evidence():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_reaction_dynamics_scattering_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["complete_36_pdf_pages_retained"]
    assert analysis["all_14_source_data_worksheets_retained"]
    assert analysis["complete_978591_nonempty_cell_surface_retained"]
    assert analysis["complete_6408_key_state_resolved_product_and_scattering_cells_retained"]
    assert analysis["source_headline_state_and_orientation_vector_retained"]
    assert analysis["experimental_theoretical_fit_normalization_estimate_tentative_and_limit_statuses_all_retained"]
    assert analysis["complete_transparent_peer_review_adverse_surface_retained"]


def test_omitted_complete_source_record_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_reaction_dynamics_scattering_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    path = ROOT / "claims/SFT-CHEM-REACTION-DYNAMICS-SCATTERING-PRODUCT-STATE-013/execution.py"
    definition = importlib.util.spec_from_file_location("kin013_execution", path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == REACTION_DYNAMICS_SCATTERING_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
