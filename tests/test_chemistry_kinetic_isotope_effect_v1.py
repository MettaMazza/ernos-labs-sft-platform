from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.kinetic_isotope_effect_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    KINETIC_ISOTOPE_EFFECT_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.kinetic_isotope_effect_law_v1 import (
    CompleteIsotopologueRatePair,
    CompleteKineticIsotopeFamily,
    ExactPositiveEventRate,
    RegisteredIsotopologuePairOccurrence,
    RetainedIsotopologuePath,
    append_isotopologue_pair_preserves_complete_family,
    forced_kinetic_isotope_effect_relation,
)
from sft.chemistry.kinetic_isotope_effect_validation_v1 import (
    _identities,
    _source_rows,
    exact_kinetic_isotope_effect_analysis,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def path(isotope: str, events: int, path_label: str = "path-a") -> RetainedIsotopologuePath:
    return RetainedIsotopologuePath(
        HeldLabel("held-isotope-reaction-identity", "reaction-a"),
        HeldLabel("held-complete-reaction-path", path_label),
        HeldLabel("held-isotopologue-identity", isotope),
        tuple(HeldLabel("registered-reaction-path-role", role) for role in ("entry", "boundary", "event", "product")),
        HeldLabel("held-isotope-reaction-condition", "condition-a"),
        ExactPositiveEventRate.from_counts(PositiveCount(events), PositiveCount(2)),
        HeldLabel("held-isotope-rate-status", "retained"),
    )


def pair(label: str, first_events: int, second_events: int, second_path: str = "path-a") -> CompleteIsotopologueRatePair:
    return CompleteIsotopologueRatePair(
        HeldLabel("registered-ordered-isotopologue-pair", label),
        path("light-held-label", first_events),
        path("heavy-held-label", second_events, second_path),
    )


def test_two_held_isotope_identities_force_exact_ordered_rate_quotient():
    result = forced_kinetic_isotope_effect_relation(pair("pair-a", 3, 2))
    assert result.exact_rate_ratio == Fraction(3, 2)
    assert result.ratio_orientation.label == "numerator-rate-greater"
    assert result.numerator_isotopologue != result.denominator_isotopologue


def test_normal_inverse_equal_and_successor_are_exact_and_structure_preserving():
    normal = forced_kinetic_isotope_effect_relation(pair("pair-a", 3, 2))
    inverse = forced_kinetic_isotope_effect_relation(pair("pair-b", 2, 3))
    equal = forced_kinetic_isotope_effect_relation(pair("pair-c", 2, 2))
    assert tuple(result.exact_rate_ratio for result in (normal, inverse, equal)) == (Fraction(3, 2), Fraction(2, 3), Fraction(1, 1))
    family = CompleteKineticIsotopeFamily((RegisteredIsotopologuePairOccurrence(PositiveCount(1), pair("pair-a", 3, 2)),))
    assert append_isotopologue_pair_preserves_complete_family(
        family, RegisteredIsotopologuePairOccurrence(PositiveCount(2), pair("pair-b", 2, 3))
    )


def test_collapsed_isotope_identity_and_mismatched_path_are_rejected():
    with pytest.raises(InadmissibleExactValue):
        CompleteIsotopologueRatePair(
            HeldLabel("registered-ordered-isotopologue-pair", "collapsed"),
            path("same-held-label", 3),
            path("same-held-label", 2),
        )
    with pytest.raises(InadmissibleExactValue):
        pair("mismatched", 3, 2, "different-path")


def test_literal_grammar_contains_256_forms_and_one_named_survivor():
    rows = candidate_rows(KINETIC_ISOTOPE_EFFECT_SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert sum(row["candidate_id"] == survivor_id(KINETIC_ISOTOPE_EFFECT_SPEC) for row in rows) == 1


def test_value_free_71_identity_registry_precedes_complete_target_surface():
    identities = _identities(ROOT)
    source_rows = _source_rows(ROOT)
    assert len(identities) == len(source_rows) == 71
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert all("target_payload" not in row and "target_payload_hash" not in row for row in identities)
    assert all("target_payload_hash" in row for row in source_rows)


def test_complete_external_vector_retains_values_replicates_controls_and_adverse_evidence():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_kinetic_isotope_effect_analysis(_source_rows(ROOT), primary)
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    assert analysis["complete_47_pdf_pages_retained"]
    assert analysis["all_23_source_data_worksheets_retained"]
    assert analysis["complete_923260_nonempty_cell_surface_retained"]
    assert analysis["complete_90_rate_ratio_vector_retained"]
    assert analysis["complete_three_direct_decay_KIE_vector_retained"]
    assert analysis["normal_inverse_and_near_unity_external_inscriptions_all_retained"]
    assert analysis["all_three_independent_experiments_and_replicates_retained_without_averaging"]
    assert analysis["infrared_limitation_reviewer_challenges_and_controls_retained"]


def test_omitted_complete_source_record_is_an_explicit_halt():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    with pytest.raises(ValueError):
        exact_kinetic_isotope_effect_analysis(_source_rows(ROOT)[:-1], primary)


def test_execution_is_capability_closed_and_independent_validator_is_distinct():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in serialized
    assert "filesystem" not in serialized and "network" not in serialized and "subprocess" not in serialized
    execution_path = ROOT / "claims/SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012/execution.py"
    definition = importlib.util.spec_from_file_location("kin012_execution", execution_path)
    module = importlib.util.module_from_spec(definition)
    assert definition and definition.loader
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == KINETIC_ISOTOPE_EFFECT_SPEC.claim_id
    assert len(execution.program.generate_candidates().candidates) == 256
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
