from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.atomic_field_splitting_successor_laws_v1 import (
    ATOMIC_FIELD_SPLITTING_SPEC,
    linear_stark_magnitude,
    magnetic_sublevel_count,
    quadratic_stark_magnitude,
    zeeman_shift_magnitude,
)
from sft.physics.atomic_field_splitting_successor_validation_v1 import (
    MEASURED_LABEL,
    field_splitting_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_angular_support_forces_two_J_plus_one():
    assert tuple(magnetic_sublevel_count(value) for value in range(1, 7)) == (2, 3, 4, 5, 6, 7)


def test_field_scaling_and_degeneracy_classes_are_exact():
    field = Fraction(2, 5)
    assert zeeman_shift_magnitude(Fraction(3, 2), 2, 2 * field) == 2 * zeeman_shift_magnitude(Fraction(3, 2), 2, field)
    assert linear_stark_magnitude(Fraction(4, 7), 2 * field) == 2 * linear_stark_magnitude(Fraction(4, 7), field)
    assert quadratic_stark_magnitude(Fraction(4, 7), 2 * field) == 4 * quadratic_stark_magnitude(Fraction(4, 7), field)


def test_complete_postseal_NIST_NBS_vector_passes():
    assert field_splitting_classification(ROOT) == MEASURED_LABEL


def test_observational_provenance_and_distinct_Stark_orders_are_retained():
    assert len(ATOMIC_FIELD_SPLITTING_SPEC.axes) == 10
    assert ATOMIC_FIELD_SPLITTING_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    order_axis = next(axis for axis in ATOMIC_FIELD_SPLITTING_SPEC.axes if axis.key == "order")
    assert order_axis.survivor.name == "degeneracy-typed-response-order"


def test_formal_module_contains_no_measurement_or_source_access():
    source = (ROOT / "sft/physics/atomic_field_splitting_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("0.46686", "1500", "750", "read_text", "source_path"):
        assert forbidden not in source
