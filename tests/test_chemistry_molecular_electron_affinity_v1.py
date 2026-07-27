from fractions import Fraction
import json
from pathlib import Path

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_electron_affinity_batch_v1 import MOLECULAR_ELECTRON_AFFINITY_SPEC
from sft.chemistry.molecular_electron_affinity_law_v1 import (
    EXACT_RESULT,
    exact_electron_affinity_difference,
)
from sft.chemistry.molecular_electron_affinity_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def ratio(value: int) -> PositiveRatio:
    return PositiveRatio.from_pair(value, 1)


def test_bound_and_unbound_orders_use_one_positive_take_law() -> None:
    bound = exact_electron_affinity_difference(ratio(8), ratio(3))
    unbound = exact_electron_affinity_difference(ratio(3), ratio(8))
    assert bound.state_order_orientation.label == "anion-below-neutral-bound-attachment"
    assert unbound.state_order_orientation.label == "anion-above-neutral-unbound-autodetachment"
    assert isinstance(bound.magnitude, PositiveRatio) and bound.magnitude.fraction == Fraction(5, 1)
    assert isinstance(unbound.magnitude, PositiveRatio) and unbound.magnitude == bound.magnitude


def test_coincident_state_uses_structural_empty_one() -> None:
    result = exact_electron_affinity_difference(ratio(3), ratio(3))
    assert result.state_order_orientation.label == "coincident-no-affinity-distinction"
    assert isinstance(result.magnitude, EmptyOne)


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(
        MOLECULAR_ELECTRON_AFFINITY_SPEC, "sha256:" + "8" * 64
    )
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MOLECULAR_ELECTRON_AFFINITY_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_value_or_state_order_orientation() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {
        "source_orientation_glyph", "fold_state_order_orientation", "magnitude_inscription",
        "exact_positive_magnitude", "uncertainty_inscription", "exact_positive_uncertainty",
        "display_magnitude_lower", "display_magnitude_upper",
    }
    assert document["all_values_and_state_order_orientations_absent"] is True
    assert len(document["rows"]) == 96
    assert all(row["target_value_and_orientation_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_value_free_page_manifest_preserves_complete_molecular_surface() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_source_page_manifest_v1.json").read_text(encoding="utf-8")
    )
    assert document["catalog_row_count"] == 192
    assert document["atomic_rows_excluded"] == 30
    assert document["molecular_page_count"] == len(document["pages"]) == 162
    assert document["all_measurement_values_and_orientations_absent"] is True
    assert all("magnitude" not in json.dumps(row).casefold() and "orientation" not in json.dumps(row).casefold() for row in document["pages"])


def test_prediction_is_target_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    targets = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_withheld_targets_v1.json").read_text(encoding="utf-8")
    )
    program_text = json.dumps(document, sort_keys=True)
    assert all(str(row["magnitude_inscription"]) not in program_text for row in targets["rows"])
    assert all(str(row["fold_state_order_orientation"]) not in program_text for row in targets["rows"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 96


def test_complete_nist_molecular_vector_reconstructs_exactly() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == 96
    assert len({row["target_id"] for row in rows}) == 96
    assert tuple(row["measured_vector_ordinal"] for row in rows) == tuple(range(1, 97))
    assert sum(row["fold_state_order_orientation"].startswith("anion-below") for row in rows) == 93
    assert sum(row["fold_state_order_orientation"].startswith("anion-above") for row in rows) == 3
    assert sum(row["uncertainty_inscription"] is not None for row in rows) == 89
    assert all(isinstance(row["vault_word"].cells[1], PositiveRatio) for row in rows)
