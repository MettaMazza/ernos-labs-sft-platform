from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.temperature_dependence_batch_v1 import TEMPERATURE_DEPENDENCE_SPEC
from sft.chemistry.temperature_dependence_law_v1 import (
    TemperatureRateRow, complete_row_append_preserves_relation, external_positive_magnitude,
    forced_temperature_dependence,
)
from sft.chemistry.temperature_dependence_validation_v1 import (
    _identities, _source_rows, exact_temperature_dependence_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def row(target: int, condition: int, reaction: str, temperature: int, rate: int) -> TemperatureRateRow:
    return TemperatureRateRow(
        HeldLabel("registered-reaction", reaction), HeldLabel("complete-condition", f"c-{condition}"),
        PositiveRatio.from_pair(temperature, 1), PositiveRatio.from_pair(rate, 1),
        PositiveCount(condition), PositiveCount(target), (PositiveRatio.from_pair(1, 2), EmptyOne()),
    )


def test_complete_exact_table_retains_source_order() -> None:
    relation = forced_temperature_dependence((row(1, 1, "a", 3, 5), row(2, 2, "a", 7, 4)))
    assert tuple(item[5].value for item in relation.ordered_rows) == (1, 2)


def test_reactions_and_unfavorable_response_remain_distinct() -> None:
    relation = forced_temperature_dependence((row(1, 1, "a", 3, 5), row(2, 2, "b", 7, 4)))
    assert {item[0].label for item in relation.ordered_rows} == {"a", "b"}
    assert relation.ordered_rows[1][2].fraction == Fraction(4)


def test_complete_append_preserves_prior_trace() -> None:
    assert complete_row_append_preserves_relation((row(1, 1, "a", 3, 5),), row(2, 2, "a", 7, 4))


def test_duplicate_target_row_and_negative_external_value_reject() -> None:
    with pytest.raises(InadmissibleExactValue):
        forced_temperature_dependence((row(1, 1, "a", 3, 5), row(1, 2, "a", 7, 4)))
    with pytest.raises(InadmissibleExactValue):
        external_positive_magnitude("-1")


def test_complete_value_free_identity_surface() -> None:
    rows = _identities(ROOT)
    assert len(rows) == 19
    assert all("rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription" not in item for item in rows)


def test_complete_primary_table_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/kin-003-temperature-dependence-v1/temperature-dependence-primary-records-v1.json").read_text())
    analysis = exact_temperature_dependence_analysis(rows, primary)
    assert analysis["all_nineteen_targets_retained_in_source_order"]
    assert analysis["both_registered_reactions_retained"]
    assert analysis["all_fourteen_condition_rows_and_nine_absences_retained"]


def test_prediction_contains_identities_not_values() -> None:
    serialized = json.dumps(prediction_program_document(ROOT), sort_keys=True)
    assert "6.0E-11" not in serialized
    assert "SFT-CHEM-KIN-003-TEMPERATURE-RATE-0001" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path = ROOT / "claims/SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003/execution.py"
    definition = importlib.util.spec_from_file_location("kin003_execution_test", path)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == TEMPERATURE_DEPENDENCE_SPEC.claim_id
