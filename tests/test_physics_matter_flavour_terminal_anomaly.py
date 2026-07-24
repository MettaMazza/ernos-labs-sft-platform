from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.matter_flavour_terminal_anomaly_laws_v1 import (
    ELECTRON_SPEC,
    MUON_SPEC,
    TURN_SPEC,
    electron_anomaly_retention,
    electron_loop_carrier,
    muon_generation_correction,
    terminal_electron_anomaly,
    terminal_muon_anomaly,
    terminal_turn_projection,
    terminal_turn_support,
)
from sft.physics.matter_flavour_terminal_anomaly_validation_v1 import (
    ELECTRON_LABEL,
    MUON_LABEL,
    anomaly_classification,
    authoritative_record,
    source_interval,
)
from sft.physics.atomic_constants import inverse_fine_structure


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_turn_and_anomaly_relations_are_exact_and_positive():
    alpha = Fraction(1, 1) / inverse_fine_structure()
    assert terminal_turn_support() == 16
    assert terminal_turn_projection() == Fraction(355, 113)
    assert electron_anomaly_retention() + alpha * electron_loop_carrier() == Fraction(1, 1)
    assert electron_loop_carrier() > Fraction(1, 10)
    assert terminal_muon_anomaly() == terminal_electron_anomaly() + muon_generation_correction()
    assert terminal_muon_anomaly() > terminal_electron_anomaly() > Fraction(1, 10000)


def test_anomaly_grammars_are_complete_observational_prediction_protocols():
    assert len(TURN_SPEC.axes) == 9
    assert len(ELECTRON_SPEC.axes) == len(MUON_SPEC.axes) == 10
    assert TURN_SPEC.provenance == ELECTRON_SPEC.provenance == MUON_SPEC.provenance == (
        ProvenanceClass.OBSERVATIONAL_DERIVATION,
    )


def test_formal_anomaly_module_has_no_measurement_target_values_or_source_access():
    source = (ROOT / "sft/physics/matter_flavour_terminal_anomaly_laws_v1.py").read_text(encoding="utf-8")
    assert "0.00115965218046" not in source
    assert "0.001165920715" not in source
    assert "source_interval" not in source
    assert "read_text" not in source


def test_terminal_anomaly_predictions_are_inside_complete_registered_intervals():
    electron_interval = source_interval(ROOT, "electron")
    muon_interval = source_interval(ROOT, "muon")
    assert electron_interval[0] <= terminal_electron_anomaly() <= electron_interval[1]
    assert muon_interval[0] <= terminal_muon_anomaly() <= muon_interval[1]
    assert anomaly_classification(ROOT, "electron") == ELECTRON_LABEL
    assert anomaly_classification(ROOT, "muon") == MUON_LABEL


def test_terminal_anomaly_source_record_declares_empirical_prediction_custody():
    custody = authoritative_record(ROOT)["custody"]
    assert custody["empirical_prediction_protocol"] is True
    assert custody["target_inaccessible_during_prediction_execution"] is True
    assert custody["formal_relation_contains_measurement"] is False
    assert custody["measurement_selects_formal_survivor"] is False
    assert custody["engine_prediction_sealed_before_target_release_within_run"] is True
