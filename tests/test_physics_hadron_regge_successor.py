from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.hadron_regge_successor_laws_v1 import (
    HADRON_REGGE_SPEC,
    affine_regge_carrier,
    baryon_multiplet_partition,
    meson_multiplet_partition,
    trajectory_multiplicity,
)
from sft.physics.hadron_regge_successor_validation_v1 import (
    MEASURED_LABEL,
    exact_common_step_exists,
    hadron_regge_classification,
    measurement_analysis,
    successive_squared_mass_steps,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_light_flavour_multiplets_are_forced_exactly():
    assert meson_multiplet_partition() == {"ordered_support": 9, "predecessor_multiplet": 8, "invariant_singlet": 1}
    assert baryon_multiplet_partition() == {"ordered_support": 27, "symmetric": 10, "mixed_first_hand": 8, "mixed_second_hand": 8, "antisymmetric": 1}


def test_affine_support_and_binary_multiplicity_are_depth_independent():
    anchor, step = Fraction(7, 11), Fraction(13, 17)
    values = tuple(affine_regge_carrier(anchor, step, rank) for rank in range(1, 129))
    assert all(successor - previous == step for previous, successor in zip(values, values[1:]))
    assert tuple(trajectory_multiplicity(depth) for depth in range(1, 8)) == (2, 4, 8, 16, 32, 64, 128)


def test_complete_postseal_PDG_vector_retains_adverse_exact_spacing_result():
    assert hadron_regge_classification(ROOT) == MEASURED_LABEL
    assert len(successive_squared_mass_steps(ROOT)) == 4
    assert exact_common_step_exists(ROOT) is False
    analysis = measurement_analysis(ROOT)
    assert len(analysis["trajectory_rows"]) == 5
    assert analysis["no_fit_performed"] is True


def test_observational_provenance_and_no_free_correction_are_retained():
    assert len(HADRON_REGGE_SPEC.axes) == 10
    assert HADRON_REGGE_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    extension = next(axis for axis in HADRON_REGGE_SPEC.axes if axis.key == "extension")
    assert extension.survivor.name == "no-extra-rule"


def test_formal_module_contains_no_measurement_or_source_access():
    source = (ROOT / "sft/physics/hadron_regge_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("775.26", "1318.2", "1688.8", "1967", "2330", "read_text", "source_path"):
        assert forbidden not in source
