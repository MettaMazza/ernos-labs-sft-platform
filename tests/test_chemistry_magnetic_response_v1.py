from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.magnetic_response_batch_v1 import MAGNETIC_RESPONSE_SPEC
from sft.chemistry.magnetic_response_law_v1 import (
    EXACT_RESULT, MolecularMagneticResponseCarrier, exact_moment_ratio,
    exact_orientation_excess, exact_susceptibility_ratio,
    repeated_response_preserves_susceptibility,
)
from sft.chemistry.magnetic_response_validation_v1 import _prediction_map, _source_rows, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_exact_orientation_closure_moment_and_susceptibility() -> None:
    a = HeldLabel("magnetic-orientation", "fibre-a")
    b = HeldLabel("magnetic-orientation", "fibre-b")
    orientation, closed = exact_orientation_excess(PositiveCount(3), PositiveCount(3), a, b)
    assert orientation.label == "balanced-closed"
    assert isinstance(closed, EmptyOne)
    orientation, retained = exact_orientation_excess(PositiveCount(5), PositiveCount(2), a, b)
    assert orientation.label == "fibre-a" and isinstance(retained, PositiveCount) and retained.value == 3
    moment = exact_moment_ratio(PositiveCount(3), PositiveCount(2))
    assert moment.fraction == Fraction(3, 2)
    assert exact_susceptibility_ratio(moment, PositiveCount(5)).fraction == Fraction(3, 10)
    assert repeated_response_preserves_susceptibility(moment, PositiveCount(5), PositiveCount(7))


def test_invalid_orientation_or_count_halts() -> None:
    a = HeldLabel("magnetic-orientation", "fibre-a")
    with pytest.raises(InadmissibleExactValue):
        exact_orientation_excess(PositiveCount(2), PositiveCount(1), a, a)
    with pytest.raises(InadmissibleExactValue):
        exact_orientation_excess(PositiveCount(2), PositiveCount(1), a, HeldLabel("signed-number", "minus"))


def test_complete_carrier_retains_molecule_state_and_support() -> None:
    carrier = MolecularMagneticResponseCarrier(
        HeldLabel("molecular-identity", "held-molecule"), HeldLabel("molecular-state", "held-state"),
        HeldLabel("angular-support", "held-rotation"), HeldLabel("spin-support", "held-spin"),
        HeldLabel("orbital-support", "held-orbital"), HeldLabel("magnetic-field-orientation", "field-a"),
        HeldLabel("magnetic-response-orientation", "response-a"),
        HeldLabel("held-magnetic-response-unit", "source-unit"), HeldLabel("measurement-condition", "source-condition"),
    )
    assert carrier.molecule.label == "held-molecule"
    with pytest.raises(InadmissibleExactValue):
        MolecularMagneticResponseCarrier(
            carrier.molecule, carrier.molecular_state, carrier.angular_support, carrier.spin_support,
            carrier.orbital_support, HeldLabel("signed-number", "negative"), carrier.response_orientation,
            carrier.response_unit, carrier.observation_condition,
        )


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(MAGNETIC_RESPONSE_SPEC, "sha256:" + "c" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MAGNETIC_RESPONSE_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_value_presence_or_orientation() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/magnetic_response_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_orientation"}
    assert document["all_magnetic_values_and_orientations_absent"] is True
    assert len(document["rows"]) == 174
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    assert not any(instruction["opcode"] == "ratio" for instruction in document["instructions"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 174


def test_complete_magnetic_vector_preserves_values_blanks_and_orientations() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == len({row["target_id"] for row in rows}) == 174
    assert sum(isinstance(row["vault_value"], PositiveRatio) for row in rows) == 136
    assert sum(isinstance(row["vault_value"], EmptyOne) for row in rows) == 38
    assert sum(row["database"] == "diatomic-reference-pdf" for row in rows) == 22
    assert any(row["source_orientation"] == "source-opposed" for row in rows)
    assert any(row["source_orientation"] == "source-aligned" for row in rows)
    assert not any(
        "χ" in row["magnetic_parameter"]
        and any(unit in row["magnetic_parameter"].casefold() for unit in ("mhz", "khz", "cm^-1"))
        for row in rows
    )


def test_complete_source_boundary_is_explicit() -> None:
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/prop-012-magnetic-response-v1/magnetic-response-primary-records-v1.json").read_text(encoding="utf-8"))
    assert primary["complete_declared_molecule_count"] == 267
    assert primary["complete_holding_group_count"] == 215
    assert primary["retrieved_constants_page_count"] == 94
    assert primary["official_linked_unavailable_page_count"] == 121
    assert primary["diatomic_reference_pdf"]["pdf_page_count"] == 162
    assert primary["diatomic_reference_pdf_target_count"] == 22
    assert primary["complete_target_cell_count"] == 174
