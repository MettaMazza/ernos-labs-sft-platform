from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_polarizability_batch_v1 import MOLECULAR_POLARIZABILITY_SPEC
from sft.chemistry.molecular_polarizability_law_v1 import (
    EXACT_RESULT,
    PolarizabilityComponent,
    exact_isotropic_response,
    repeated_equal_field_response,
)
from sft.chemistry.molecular_polarizability_validation_v1 import (
    _prediction_map,
    _source_rows,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def component(axis: str, response: int, field: int) -> PolarizabilityComponent:
    return PolarizabilityComponent(
        HeldLabel("molecular-response-axis", axis),
        PositiveRatio.from_pair(response, 1),
        PositiveRatio.from_pair(field, 1),
    )


def test_exact_response_ratio_and_equal_act_successor() -> None:
    item = component("a", 6, 2)
    assert item.exact_response.fraction == Fraction(3, 1)
    repeated = repeated_equal_field_response(item, PositiveCount(9))
    assert repeated.exact_response == item.exact_response


def test_exact_three_axis_isotropic_composition() -> None:
    components = (component("a", 2, 1), component("b", 6, 2), component("c", 12, 3))
    assert exact_isotropic_response(components).fraction == Fraction(3, 1)
    with pytest.raises(InadmissibleExactValue):
        exact_isotropic_response(components[:2])
    with pytest.raises(InadmissibleExactValue):
        exact_isotropic_response((components[0], components[0], components[2]))


def test_invalid_component_family_halts() -> None:
    with pytest.raises(InadmissibleExactValue):
        PolarizabilityComponent(
            HeldLabel("not-a-response-axis", "a"),
            PositiveRatio.from_pair(1, 1),
            PositiveRatio.from_pair(1, 1),
        )


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(
        MOLECULAR_POLARIZABILITY_SPEC, "sha256:" + "6" * 64
    )
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MOLECULAR_POLARIZABILITY_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_alpha_value() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_polarizability_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {"value", "display_rounding_lower", "display_rounding_upper", "inscription"}
    assert document["all_polarizability_values_absent"] is True
    assert len(document["rows"]) == 252
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    targets = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_polarizability_withheld_targets_v1.json").read_text(encoding="utf-8")
    )
    program_text = json.dumps(document, sort_keys=True)
    assert all(str(row["inscription"]) not in program_text for row in targets["rows"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    assert len(_prediction_map(execution.output)) == 252


def test_complete_nist_molecular_vector_reconstructs_exactly() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == 252
    assert len({row["target_id"] for row in rows}) == 252
    assert tuple(row["source_row_ordinal"] for row in rows) == tuple(range(1, 253))
    assert len({row["reference"] for row in rows}) == 10
    assert all(row["vault_value"].fraction > 0 for row in rows)
    assert rows[0]["formula"] == "D2"
    assert rows[-1]["formula"] == "C60"
