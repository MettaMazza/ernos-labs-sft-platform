from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.atomic_spectra_completion_laws_v1 import (
    ATOMIC_SPECS,
    atomic_scale_hierarchy,
    cubic_balance,
    cubic_coordination,
    cubic_neighbour_weight,
    gross_atomic_scale,
    hydrogen_level,
    hydrogen_transition,
    molecular_spectrum_hierarchy,
    transition_selection,
)


ROOT = Path(__file__).resolve().parents[1]


def test_cubic_atomic_support_closes_exactly():
    assert cubic_coordination() == 6
    assert cubic_neighbour_weight() == Fraction(1, 12)
    assert cubic_balance() == Fraction(1, 2)


def test_hydrogen_spectrum_is_depth_independent_and_exact():
    assert tuple(hydrogen_level(n) for n in range(1, 6)) == (
        Fraction(1, 1), Fraction(1, 4), Fraction(1, 9), Fraction(1, 16), Fraction(1, 25)
    )
    assert hydrogen_transition(2, 1) == Fraction(3, 4)
    assert hydrogen_transition(3, 2) == Fraction(5, 36)


def test_atomic_correction_and_molecular_hierarchies_are_ordered():
    hierarchy = atomic_scale_hierarchy()
    assert hierarchy["gross"] > hierarchy["fine"] > hierarchy["lamb"]
    assert gross_atomic_scale() > Fraction(1, 100000)
    molecular = molecular_spectrum_hierarchy()
    assert molecular["molecular_rotation_vibration"] == Fraction(1, 4)
    assert molecular["two_molecular_quanta"] == molecular["electronic"]


def test_transition_counts_and_formal_provenance_are_complete():
    selection = transition_selection()
    assert selection["orbital_step"] == 1
    assert selection["magnetic_orientations"] == 2
    assert selection["complete_spatial_orientations"] == 6
    assert all(len(spec.axes) == 8 for spec in ATOMIC_SPECS)
    assert all(spec.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,) for spec in ATOMIC_SPECS)


def test_atomic_formal_module_contains_no_measurement_target():
    source = (ROOT / "sft/physics/atomic_spectra_completion_laws_v1.py").read_text(encoding="utf-8")
    for target in ("13.598433", "109678.7717", "1215", "6562", "4861"):
        assert target not in source
    assert "read_text" not in source
