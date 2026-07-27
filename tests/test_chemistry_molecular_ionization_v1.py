from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_ionization_batch_v1 import MOLECULAR_IONIZATION_SPEC
from sft.chemistry.molecular_ionization_law_v1 import (
    EXACT_RESULT,
    least_adiabatic_take,
    ordered_ionization_take,
    vertical_not_below_adiabatic,
)
from sft.chemistry.molecular_ionization_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def ratio(value: int) -> PositiveRatio:
    return PositiveRatio.from_pair(value, 1)


def test_ordered_take_adiabatic_least_and_vertical_order() -> None:
    initial = ratio(3)
    terminals = (ratio(8), ratio(6), ratio(7))
    assert ordered_ionization_take(terminals[0], initial).fraction == Fraction(5, 1)
    assert least_adiabatic_take(initial, terminals).fraction == Fraction(3, 1)
    assert vertical_not_below_adiabatic(initial, terminals, terminals[2]) is True


def test_invalid_terminal_order_and_incomplete_vertical_support_halt() -> None:
    initial = ratio(3)
    terminals = (ratio(6), ratio(7))
    with pytest.raises(InadmissibleExactValue):
        ordered_ionization_take(initial, terminals[0])
    with pytest.raises(InadmissibleExactValue):
        least_adiabatic_take(initial, ())
    with pytest.raises(InadmissibleExactValue):
        vertical_not_below_adiabatic(initial, terminals, ratio(8))


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(
        MOLECULAR_IONIZATION_SPEC, "sha256:" + "7" * 64
    )
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MOLECULAR_IONIZATION_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_ionization_value() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_ionization_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {"value", "lower", "upper", "inscription", "uncertainty", "uncertainty_inscription"}
    assert document["all_ionization_values_absent"] is True
    assert len(document["rows"]) == 9
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    targets = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_ionization_withheld_targets_v1.json").read_text(encoding="utf-8")
    )
    program_text = json.dumps(document, sort_keys=True)
    assert all(str(row["inscription"]) not in program_text for row in targets["rows"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 9


def test_complete_nist_diatomic_vector_reconstructs_exactly() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == 9
    assert len({row["target_id"] for row in rows}) == 9
    assert tuple(row["source_row_ordinal"] for row in rows) == tuple(range(1, 10))
    assert tuple(row["formula"] for row in rows) == ("D2", "HD", "H2", "N2", "CO", "NO", "O2", "HF", "F2")
    assert sum(row["uncertainty"] is not None for row in rows) == 7
    assert all(row["vault_value"].fraction > 0 for row in rows)
