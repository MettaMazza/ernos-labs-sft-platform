import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.entropy_multiplicity_correspondence_batch_v1 import ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC
from sft.chemistry.entropy_multiplicity_correspondence_law_v1 import (
    append_microstate_preserves_ledger, chemical_entropy_ledger, chemical_observation_refines,
    closed_distinction_pairs,
)
from sft.chemistry.entropy_multiplicity_correspondence_validation_v1 import (
    EntropyMultiplicityCorrespondenceValidator, _prediction_map, exact_entropy_phase_analysis,
    prediction_program_document,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.internal_energy_composition_validation_v1 import VALUE_COLUMNS, _source_rows
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, fold_program_from_mapping
from sft.engine.exact import HeldLabel, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def support_and_observations():
    support = tuple(HeldLabel("chemical-microstate", label) for label in ("aa", "ab", "ba", "bb"))
    fine = tuple((state, HeldLabel("chemical-macro-observation", state.label)) for state in support)
    prefix = tuple((state, HeldLabel("chemical-macro-observation", state.label[0])) for state in support)
    coarse = tuple((state, HeldLabel("chemical-macro-observation", "unresolved")) for state in support)
    return support, fine, prefix, coarse


def test_exact_multiplicity_and_complete_pair_ledgers() -> None:
    support, _, prefix, coarse = support_and_observations()
    prefix_ledger = chemical_entropy_ledger(support, prefix)
    assert all(item.multiplicity == PositiveCount(2) and item.exact_support_part.fraction.numerator == 1 and item.exact_support_part.fraction.denominator == 2 for item in prefix_ledger.classes)
    assert len(closed_distinction_pairs(chemical_entropy_ledger(support, coarse))) == 6


def test_singleton_certainty_is_structural_EmptyOne() -> None:
    support, fine, _, _ = support_and_observations()
    assert all(isinstance(item.unresolved_distinctions, EmptyOne) for item in chemical_entropy_ledger(support, fine).classes)


def test_refinement_and_successor_are_depth_independent() -> None:
    support, fine, prefix, coarse = support_and_observations()
    assert chemical_observation_refines(support, fine, prefix)
    assert chemical_observation_refines(support, prefix, coarse)
    assert append_microstate_preserves_ledger(
        support, prefix, HeldLabel("chemical-microstate", "ac"), HeldLabel("chemical-macro-observation", "a")
    )


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC)
    assert closure.scope.value == "depth_independent"


def test_entropy_identity_registry_is_value_free() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json").read_text())
    forbidden = set(VALUE_COLUMNS) | {"snapshot_hash", "target_payload", "target_payload_hash"}
    assert len(document["rows"]) == 13
    assert all(not forbidden.intersection(row) for row in document["rows"])


def test_prediction_contains_no_scalar_entropy_phase_or_transition_values() -> None:
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in ("entropy-joule-per-mole-kelvin", "enthalpy-kilojoule-per-mole", "temperature-kelvin", "phase-identity"):
        assert forbidden not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")},
    )
    assert len(_prediction_map(execution.output)) == 13


def test_complete_external_entropy_and_phase_transition_vector_is_exact() -> None:
    analysis = exact_entropy_phase_analysis(_source_rows(ROOT))
    assert len(analysis["entropy_values_joule_per_mole_kelvin"]) == 13
    assert len(analysis["adjacent_exact_positive_entropy_steps"]) == 12
    assert all(bool(value) for key, value in analysis.items() if not isinstance(value, tuple))


def test_postseal_validator_preserves_all_rows_values_and_controls() -> None:
    result = EntropyMultiplicityCorrespondenceValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 22
