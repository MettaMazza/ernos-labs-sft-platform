import json
from pathlib import Path

import pytest

from sft.chemistry.cross_property_batch_v1 import CROSS_PROPERTY_SPEC
from sft.chemistry.cross_property_law_v1 import (
    EXACT_RESULT, CrossPropertyMolecularCarrier, ExactPropertyProjection,
    compose_exact_property_vector, lawful_projection_extension_preserves_existing,
    project_exact_property,
)
from sft.chemistry.cross_property_validation_v1 import _prediction_map, _source_rows, prediction_program_document
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def projection(label: str, value: int) -> ExactPropertyProjection:
    return ExactPropertyProjection(
        HeldLabel("molecular-property-family", label), HeldLabel("admitted-property-relation", label + "-law"),
        HeldLabel("property-result-orientation", "exact-positive"), PositiveRatio.from_pair(value, 1),
    )


def carrier(properties: tuple[ExactPropertyProjection, ...]) -> CrossPropertyMolecularCarrier:
    return CrossPropertyMolecularCarrier(
        HeldLabel("structural-molecular-carrier", "H2"), HeldLabel("molecular-constitution", "held"),
        HeldLabel("molecular-state", "ground"), HeldLabel("held-charge-identity", "neutral"),
        HeldLabel("geometry-symmetry-carrier", "held"), HeldLabel("measurement-condition", "registered"),
        tuple(item.property_family for item in properties),
    )


def test_one_carrier_projection_and_depth_independent_extension() -> None:
    p1, p2, p3 = projection("bond", 2), projection("vibration", 3), projection("formation", 5)
    vector = compose_exact_property_vector(carrier((p1, p2)), (p1, p2))
    assert project_exact_property(vector, p1.property_family) == p1
    assert lawful_projection_extension_preserves_existing(carrier((p1, p2)), vector, p3)


def test_duplicate_or_incomplete_support_halts() -> None:
    p1, p2 = projection("bond", 2), projection("vibration", 3)
    with pytest.raises(InadmissibleExactValue):
        compose_exact_property_vector(carrier((p1, p2)), (p1, p1))
    with pytest.raises(InadmissibleExactValue):
        compose_exact_property_vector(carrier((p1, p2)), (p1,))


def test_candidate_grammar_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(CROSS_PROPERTY_SPEC, "sha256:" + "e" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(CROSS_PROPERTY_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_contains_no_targets_or_hashes() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/cross_property_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = {"source_target_payload", "source_target_payload_hash", "withheld_target_hash", "source_value_inscription", "native_value", "measurement_present", "external_measurement_absence"}
    assert document["complete_property_family_count"] == 13
    assert document["complete_source_identity_row_count"] == 9025
    assert document["complete_structural_carrier_count"] == 1104
    assert document["multi_property_structural_carrier_count"] == 676
    assert all(row["target_value_presence_and_orientation_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_and_target_hash_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    assert not any("source-target-payload-hash" in tuple(map(str, instruction["arguments"])) for instruction in document["instructions"])
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "test-seal")})
    assert len(_prediction_map(execution.output)) == 9025


def test_complete_cross_property_surface_and_overlap_are_preserved() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == len({row["cross_property_target_id"] for row in rows}) == 9025
    assert len({row["property_family"] for row in rows}) == 13
    assert len({row["structural_carrier_id"] for row in rows}) == 1104
    assert len({row["structural_carrier_id"] for row in rows if row["cross_property_overlap"]}) == 676
    assert sum(row["cross_property_overlap"] for row in rows) == 6676
    h2 = [row for row in rows if row["structural_carrier_id"] == "exact-formula:H2"]
    assert len({row["property_family"] for row in h2}) == 8


def test_nonjoinable_rows_are_retained_without_guessing() -> None:
    rows = _source_rows(ROOT)
    rules = {"no-explicit-species-formula-in-registered-diatomic-PDF-cell", "source-species-label-not-formula-normalized", "bound-composite-not-conflated-with-constituent-molecule"}
    nonjoined = [row for row in rows if row["carrier_derivation_rule"] in rules]
    assert nonjoined
    assert all(not row["structural_carrier_id"].startswith("exact-formula:") for row in nonjoined)
