from fractions import Fraction
from pathlib import Path

from sft.physics.matter_flavour_terminal_ckm_validation_v1 import (
    TERMINAL_CKM_LABEL,
    TERMINAL_ETA_LABEL,
    authoritative_record,
    terminal_ckm_classification,
    terminal_ckm_prediction_intervals,
    terminal_eta_classification,
    terminal_eta_prediction_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_ckm_exact_complete_comparison():
    prediction = terminal_ckm_prediction_intervals()
    assert set(prediction) == {
        "s12_squared",
        "s23_squared",
        "s13_squared",
        "jarlskog_squared",
    }
    assert terminal_ckm_classification(ROOT) == TERMINAL_CKM_LABEL


def test_terminal_eta_is_sealed_prediction_inside_both_registered_routes():
    prediction = terminal_eta_prediction_interval()
    assert Fraction("0.00000000058") < prediction[0] <= prediction[1] < Fraction("0.00000000063")
    assert terminal_eta_classification(ROOT) == TERMINAL_ETA_LABEL


def test_terminal_source_discloses_observational_derivation():
    custody = authoritative_record(ROOT)["custody"]
    assert custody["development_target_already_known"] is True
    assert custody["classification"] == "observational_derivation"
    assert custody["formal_relation_contains_measurement"] is False
    assert custody["blind_forward_discovery_claimed"] is False
