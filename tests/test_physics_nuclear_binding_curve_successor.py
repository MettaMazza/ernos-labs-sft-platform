from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (
    NUCLEAR_BINDING_CURVE_SPEC,
    binding_ledger,
    binding_peak_certificate,
    surface_deficit_share,
    tail_upper_bounds,
)
from sft.physics.nuclear_binding_curve_successor_validation_v1 import (
    MEASURED_LABEL,
    measurement_analysis,
    nuclear_binding_curve_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_zero_parameter_ledger_shares_and_terms_are_exact():
    ledger = binding_ledger(62, 28)
    assert surface_deficit_share() == Fraction(1, 5)
    assert ledger["mass_number"] == 62
    assert ledger["charge_count"] == 28
    assert ledger["neutron_count"] == 34
    assert ledger["pairing_class"] == "paired-gain"


def test_global_peak_and_unbounded_tail_are_forced():
    peak = binding_peak_certificate()
    tail = tail_upper_bounds()
    assert (peak["mass_number"], peak["charge_count"], peak["neutron_count"]) == (62, 28, 34)
    assert peak["score_lower"] > peak["rival_upper"]
    assert peak["score_lower"] > tail["low_charge_upper"]
    assert peak["score_lower"] > tail["high_charge_upper"]


def test_complete_postseal_ame2020_vector_matches_exact_coordinate():
    assert nuclear_binding_curve_classification(ROOT) == MEASURED_LABEL
    analysis = measurement_analysis(ROOT)
    assert analysis["complete_measured_row_count"] == 2548
    assert analysis["formal_coordinate_matches_measurement"] is True
    assert analysis["peak_interval_separated_from_every_rival"] is True


def test_curve_direction_and_adverse_iron_only_shortcut_are_retained():
    analysis = measurement_analysis(ROOT)
    assert analysis["light_curve_rises_to_peak"] is True
    assert analysis["heavy_curve_falls_from_peak"] is True
    assert analysis["iron_only_shortcut_rejected"] is True


def test_observational_provenance_and_no_fitted_extension_are_retained():
    assert len(NUCLEAR_BINDING_CURVE_SPEC.axes) == 10
    assert NUCLEAR_BINDING_CURVE_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    extension = next(axis for axis in NUCLEAR_BINDING_CURVE_SPEC.axes if axis.key == "extension")
    assert extension.survivor.name == "no-extra-rule"
    source = (ROOT / "sft/physics/nuclear_binding_curve_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("8794.5555", "ame2020", "nickel", "source_path", "read_text"):
        assert forbidden not in source
