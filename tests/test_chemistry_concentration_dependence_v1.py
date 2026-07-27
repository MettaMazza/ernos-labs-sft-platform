from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.concentration_dependence_batch_v1 import CONCENTRATION_DEPENDENCE_SPEC
from sft.chemistry.concentration_dependence_law_v1 import (
    ConcentrationRateRow, complete_row_append_preserves_relation, external_positive_magnitude,
    forced_concentration_dependence,
)
from sft.chemistry.concentration_dependence_validation_v1 import (
    _identities, _source_rows, exact_concentration_dependence_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def row(number: int, density: int, rate: int) -> ConcentrationRateRow:
    return ConcentrationRateRow(HeldLabel("registered-reactant", "OH-DME"), HeldLabel("complete-condition", f"c-{number}"), PositiveRatio.from_pair(density, 1), PositiveRatio.from_pair(rate, 1), PositiveCount(number), (PositiveRatio.from_pair(1, 2), EmptyOne()))


def test_complete_exact_table_retains_source_order() -> None:
    relation = forced_concentration_dependence((row(1, 3, 5), row(2, 7, 4)))
    assert tuple(item[3].value for item in relation.ordered_rows) == (1, 2)


def test_unfavorable_lower_response_is_retained() -> None:
    relation = forced_concentration_dependence((row(1, 3, 5), row(2, 7, 4)))
    assert relation.ordered_rows[1][1].fraction == Fraction(4)


def test_complete_append_preserves_prior_trace() -> None:
    assert complete_row_append_preserves_relation((row(1, 3, 5),), row(2, 7, 4))


def test_duplicate_source_row_and_negative_external_value_reject() -> None:
    with pytest.raises(InadmissibleExactValue):
        forced_concentration_dependence((row(1, 3, 5), row(1, 7, 4)))
    with pytest.raises(InadmissibleExactValue):
        external_positive_magnitude("-1")


def test_complete_value_free_identity_surface() -> None:
    rows = _identities(ROOT)
    assert len(rows) == 9
    assert all("rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription" not in item for item in rows)


def test_complete_primary_table_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/kin-002-concentration-dependence-v1/concentration-dependence-primary-records-v1.json").read_text())
    analysis = exact_concentration_dependence_analysis(rows, primary)
    assert analysis["all_nine_rows_retained_in_source_order"]
    assert analysis["all_27_uncertainty_coordinates_retained"]


def test_prediction_contains_identities_not_values() -> None:
    serialized = json.dumps(prediction_program_document(ROOT), sort_keys=True)
    assert "1.7E-11" not in serialized
    assert "SFT-CHEM-KIN-002-CONCENTRATION-RATE-0001" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path = ROOT / "claims/SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002/execution.py"
    definition = importlib.util.spec_from_file_location("kin002_execution_test", path)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == CONCENTRATION_DEPENDENCE_SPEC.claim_id
