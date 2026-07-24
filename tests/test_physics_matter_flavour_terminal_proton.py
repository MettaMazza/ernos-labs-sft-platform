from fractions import Fraction
from pathlib import Path

from sft.physics.matter_flavour_terminal_proton_laws_v1 import (
    TERMINAL_PROTON_SPEC,
    composite_bulk_boundary_support,
    terminal_proton_dressing,
    terminal_proton_relation,
    terminal_proton_retention,
)
from sft.physics.matter_flavour_terminal_proton_validation_v1 import (
    EXPECTED_LABEL,
    authoritative_record,
    source_interval,
    terminal_proton_classification,
    terminal_proton_prediction_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_proton_typed_relation_closes_exactly():
    relation = terminal_proton_relation()
    assert relation["heavy_complement"] == 53
    assert composite_bulk_boundary_support() == 30
    assert relation["terminal_transport"] == Fraction(2, 135)
    assert terminal_proton_retention() + terminal_proton_dressing() == Fraction(1, 1)
    assert len(TERMINAL_PROTON_SPEC.axes) == 11


def test_terminal_proton_prediction_is_contained_in_complete_codata_interval():
    prediction = terminal_proton_prediction_interval()
    target = source_interval(ROOT)
    assert target[0] <= prediction[0] <= prediction[1] <= target[1]
    assert terminal_proton_classification(ROOT) == EXPECTED_LABEL


def test_terminal_proton_uses_observational_prediction_protocol():
    custody = authoritative_record(ROOT)["custody"]
    assert custody["empirical_prediction_protocol"] is True
    assert custody["target_inaccessible_during_prediction_execution"] is True
    assert custody["formal_relation_contains_measurement"] is False
