from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.molecular_spectroscopy_successor_laws_v1 import (
    MOLECULAR_SPECTROSCOPY_SPEC,
    adjacent_rotational_gap,
    adjacent_vibrational_gap,
    deuterium_rotational_transport,
    deuterium_vibrational_squared_transport,
    empty_rotational_ground,
    hydrogen_anharmonic_to_vibrational,
    hydrogen_rotational_to_vibrational,
    rotational_level,
)
from sft.physics.molecular_spectroscopy_successor_validation_v1 import (
    MEASURED_LABEL,
    authoritative_record,
    measured_ratio_intervals,
    molecular_spectroscopy_classification,
    sealed_ratio_vector,
)


ROOT = Path(__file__).resolve().parents[1]


def test_molecular_rotational_and_vibrational_ladders_are_exact():
    assert empty_rotational_ground() == ()
    assert tuple(rotational_level(j) for j in range(1, 5)) == (2, 6, 12, 20)
    assert tuple(adjacent_rotational_gap(j) for j in range(1, 5)) == (2, 4, 6, 8)
    gaps = tuple(
        adjacent_vibrational_gap(Fraction(1, 1), Fraction(1, 100), ordinal)
        for ordinal in (2, 3, 4)
    )
    assert gaps[0] > gaps[1] > gaps[2] > 0


def test_molecular_terminal_carriers_are_exact_distinct_and_positive():
    rotation = hydrogen_rotational_to_vibrational()
    anharmonic = hydrogen_anharmonic_to_vibrational()
    isotope_rotation = deuterium_rotational_transport()
    isotope_vibration_squared = deuterium_vibrational_squared_transport()
    assert Fraction(1, 100) < rotation < anharmonic < Fraction(1, 10)
    assert Fraction(1, 2) < isotope_rotation < isotope_vibration_squared < Fraction(3, 5)


def test_molecular_postseal_NIST_vector_passes_exactly():
    intervals = measured_ratio_intervals(ROOT)
    for key, prediction in sealed_ratio_vector().items():
        assert intervals[key][0] <= prediction <= intervals[key][1]
    assert molecular_spectroscopy_classification(ROOT) == MEASURED_LABEL


def test_molecular_provenance_and_predecessor_disposition_are_complete():
    record = authoritative_record(ROOT)
    assert len(MOLECULAR_SPECTROSCOPY_SPEC.axes) == 10
    assert MOLECULAR_SPECTROSCOPY_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    assert record["predecessor_disposition"]["immutable_leading_claim"] == "SFT-PHYS-MOLECULAR-SPECTRUM-HIERARCHY-004"
    assert "rejected" in record["predecessor_disposition"]["retained_adverse_result"]


def test_molecular_formal_module_contains_no_measurement_target_or_source_access():
    source = (ROOT / "sft/physics/molecular_spectroscopy_successor_laws_v1.py").read_text(encoding="utf-8")
    for forbidden in (
        "4401.213",
        "3115.50",
        "60.8530",
        "30.4436",
        "nist",
        "read_text",
        "SOURCE_PATH",
    ):
        assert forbidden.lower() not in source.lower()
