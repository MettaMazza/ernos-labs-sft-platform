from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.atomic_transition_rate_successor_laws_v1 import (
    ATOMIC_TRANSITION_RATE_SPEC,
    electric_multipole_exponent,
    exact_lifetime,
    normalized_electric_rate,
    successor_multipole_ratio,
)
from sft.physics.atomic_transition_rate_successor_validation_v1 import (
    MEASURED_LABEL,
    allowed_example_lifetime,
    measured_interval,
    transition_rate_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_electric_multipole_exponent_is_depth_independent():
    assert tuple(electric_multipole_exponent(rank) for rank in range(1, 5)) == (3, 5, 7, 9)
    assert all(electric_multipole_exponent(rank + 1) == electric_multipole_exponent(rank) + 2 for rank in range(1, 64))


def test_rate_lifetime_and_conditional_suppression_are_exact():
    gap, strength, weight = Fraction(3, 4), Fraction(2, 3), 3
    assert normalized_electric_rate(gap, strength, weight) == Fraction(3, 32)
    assert exact_lifetime((Fraction(1, 8), Fraction(1, 24))) == 6
    assert successor_multipole_ratio(gap) == Fraction(9, 16)


def test_complete_postseal_NIST_vector_passes():
    assert transition_rate_classification(ROOT) == MEASURED_LABEL
    allowed = allowed_example_lifetime(ROOT)
    assert measured_interval(ROOT, "nist_argon_metastable")[0] > allowed
    assert measured_interval(ROOT, "nist_aluminium_clock")[0] > allowed


def test_adverse_M1_boundary_and_provenance_are_retained():
    assert len(ATOMIC_TRANSITION_RATE_SPEC.axes) == 10
    assert ATOMIC_TRANSITION_RATE_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    forbidden_axis = next(axis for axis in ATOMIC_TRANSITION_RATE_SPEC.axes if axis.key == "forbidden")
    assert forbidden_axis.survivor.name == "typed-channel-conditional-suppression"


def test_formal_module_contains_no_measurement_or_source_access():
    source = (ROOT / "sft/physics/atomic_transition_rate_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("63800000", "20.6", "0.00939", "read_text", "source_path"):
        assert forbidden not in source
