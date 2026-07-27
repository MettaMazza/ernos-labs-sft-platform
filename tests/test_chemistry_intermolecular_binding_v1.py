from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.intermolecular_binding_batch_v1 import INTERMOLECULAR_BINDING_SPEC
from sft.chemistry.intermolecular_binding_law_v1 import (
    EXACT_RESULT,
    IntermolecularBindingCarrier,
    append_shared_constituent_preserves_binding,
    exact_intermolecular_binding_take,
    exact_separated_constituent_state,
    repeated_unit_binding,
    unbound_interaction_form,
)
from sft.chemistry.intermolecular_binding_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_exact_constituent_composition_binding_and_successors() -> None:
    separated = exact_separated_constituent_state((PositiveRatio.from_pair(5, 2), PositiveRatio.from_pair(7, 3)))
    bound = PositiveRatio.from_pair(4, 1)
    assert separated.fraction == Fraction(29, 6)
    assert exact_intermolecular_binding_take(separated, bound).fraction == Fraction(5, 6)
    assert append_shared_constituent_preserves_binding(separated, bound, PositiveRatio.from_pair(11, 5))
    assert repeated_unit_binding(separated, bound, PositiveCount(3)).fraction == Fraction(5, 2)
    assert isinstance(unbound_interaction_form(), EmptyOne)


def test_invalid_order_halts_instead_of_creating_negative_or_zero() -> None:
    with pytest.raises(InadmissibleExactValue):
        exact_intermolecular_binding_take(PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(3, 1))
    with pytest.raises(InadmissibleExactValue):
        exact_intermolecular_binding_take(PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(2, 1))
    with pytest.raises(InadmissibleExactValue):
        exact_separated_constituent_state((PositiveRatio.from_pair(2, 1),))


def test_complete_binding_carrier_retains_constituents_states_and_separation() -> None:
    carrier = IntermolecularBindingCarrier(
        (HeldLabel("molecular-constituent", "water-one"), HeldLabel("molecular-constituent", "water-two")),
        (HeldLabel("constituent-state", "ground-one"), HeldLabel("constituent-state", "ground-two")),
        HeldLabel("bound-composite", "water-dimer"),
        HeldLabel("bound-composite-state", "retained-bound-state"),
        HeldLabel("finite-separation-organization", "separated-water-pair"),
        HeldLabel("intermolecular-channel", "hydrogen-bond-channel"),
        HeldLabel("measurement-condition", "registered-condition"),
        HeldLabel("held-energy-unit", "reciprocal-centimeter"),
    )
    assert len(carrier.constituents) == len(carrier.constituent_states) == 2
    with pytest.raises(InadmissibleExactValue):
        IntermolecularBindingCarrier(
            carrier.constituents, carrier.constituent_states,
            carrier.bound_composite, carrier.bound_composite_state,
            HeldLabel("continuum-separation-coordinate", "r"),
            carrier.interaction_channel, carrier.condition, carrier.energy_unit,
        )


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(INTERMOLECULAR_BINDING_SPEC, "sha256:" + "b" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(INTERMOLECULAR_BINDING_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_binding_target_or_orientation() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/intermolecular_binding_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {
        "value_inscription_kJ_per_mol", "value_inscription_cm_inverse", "uncertainty_inscription_cm_inverse",
        "central_cm_inverse", "uncertainty_cm_inverse", "lower_cm_inverse", "upper_cm_inverse",
        "external_orientation", "absolute_inscribed_magnitude_kJ_per_mol",
    }
    assert document["all_binding_values_absent"] is True
    assert len(document["rows"]) == 1299
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    instructions = document["instructions"]
    assert not any(instruction["opcode"] == "ratio" for instruction in instructions)
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 1299


def test_complete_dimer_cluster_vector_preserves_favorable_adverse_and_measurement_classes() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == len({row["target_id"] for row in rows}) == 1299
    calculated = tuple(row for row in rows if row["source_class"] == "authoritative-calculated-benchmark")
    measured = tuple(row for row in rows if row["source_class"] == "reported-experimental-cluster-dissociation-value")
    assert len(calculated) == 1297
    assert len({row["dimer_id"] for row in calculated}) == 11
    assert len(measured) == 2
    assert sum(isinstance(row["vault_value"], PositiveRatio) for row in rows) == 1203
    assert sum(isinstance(row["vault_value"], EmptyOne) for row in rows) == 96
    assert {row["value_inscription_cm_inverse"] for row in measured} == {"1105", "1244"}


def test_complete_source_boundary_counts_are_explicit() -> None:
    primary = json.loads(
        (ROOT / "experiments/external_sources/chemistry/snapshots/prop-011-intermolecular-binding-v1/intermolecular-binding-primary-records-v1.json").read_text(encoding="utf-8")
    )
    assert primary["complete_cccbdb_dimer_count"] == 11
    assert primary["complete_cccbdb_linked_value_count"] == 1297
    assert primary["complete_cccbdb_positive_value_count"] == 1201
    assert primary["complete_cccbdb_signed_adverse_value_count"] == 96
    assert primary["complete_cccbdb_unavailable_dnf_inscription_count"] == 269
    assert primary["reported_experimental_cluster_dissociation_count"] == 2
    assert primary["ion_cluster_compendium"]["numerical_rows_used_as_targets"] is False
