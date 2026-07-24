from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.nuclear_residual_force_successor_laws_v1 import (
    NUCLEAR_RESIDUAL_FORCE_SPEC,
    inverse_mass_order,
    mediator_range,
    neutral_composite_exchange,
    residual_boundary_support,
)
from sft.physics.nuclear_residual_force_successor_validation_v1 import (
    MEASURED_LABEL,
    measurement_analysis,
    nuclear_residual_force_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_neutral_closure_and_quarter_residual_are_exact():
    assert neutral_composite_exchange()["leading_external_label"] == ()
    assert residual_boundary_support() == Fraction(1, 4)


def test_positive_mediator_range_is_exact_and_order_reversing():
    assert mediator_range(Fraction(3, 7)) == Fraction(7, 3)
    assert inverse_mass_order(Fraction(3, 7), Fraction(5, 7))
    assert all(inverse_mass_order(Fraction(rank, 19), Fraction(rank + 1, 19)) for rank in range(1, 128))


def test_complete_postseal_PDG_NIST_vector_passes_with_strength_boundary():
    assert nuclear_residual_force_classification(ROOT) == MEASURED_LABEL
    analysis = measurement_analysis(ROOT)
    assert analysis["all_scattering_intervals_positive"] is True
    assert analysis["channel_strength_intervals_disjoint"] is True
    assert analysis["one_quarter_is_structural_order_not_cross_section"] is True


def test_observational_provenance_and_no_fitted_profile_are_retained():
    assert len(NUCLEAR_RESIDUAL_FORCE_SPEC.axes) == 10
    assert NUCLEAR_RESIDUAL_FORCE_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    extension = next(axis for axis in NUCLEAR_RESIDUAL_FORCE_SPEC.axes if axis.key == "extension")
    assert extension.survivor.name == "no-extra-rule"


def test_formal_module_contains_no_measurement_or_source_access():
    source = (ROOT / "sft/physics/nuclear_residual_force_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("134.9768", "139.57039", "775.26", "782.66", "82.02", "7.640", "read_text", "source_path"):
        assert forbidden not in source
