from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.radioactive_decay_successor_laws_v1 import (
    RADIOACTIVE_DECAY_SPEC,
    alpha_representative,
    beta_representative,
    deterministic_halving_partition,
    gamma_representative,
    primitive_transition_classes,
    survival_part,
    transport_half_life,
)
from sft.physics.radioactive_decay_successor_validation_v1 import (
    MEASURED_LABEL,
    measurement_analysis,
    radioactive_decay_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_three_primitive_topologies_and_representatives_are_exact():
    assert len(primitive_transition_classes()) == 3
    assert len({alpha_representative()["primitive_class"], beta_representative()["primitive_class"], gamma_representative()["primitive_class"]}) == 3
    assert (alpha_representative()["cluster_mass_count"], alpha_representative()["cluster_charge_count"]) == (4, 2)


def test_survival_and_time_transport_are_positive_exact_parts():
    assert tuple(survival_part(rank) for rank in range(1, 4)) == (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8))
    transported = transport_half_life(Fraction(570, 100), 3)
    assert transported["elapsed_time"] == Fraction(171, 10)
    assert transported["survival_part"] == Fraction(1, 8)


def test_halving_is_a_deterministic_complete_path_partition():
    for depth in range(1, 8):
        row = deterministic_halving_partition(depth)
        assert row["complete_path_count"] == row["retained_path_count"] + row["released_path_count"]
        assert row["retained_share"] == Fraction(1, 2)


def test_complete_postseal_nubase2020_vector_maps_without_omission():
    assert radioactive_decay_classification(ROOT) == MEASURED_LABEL
    analysis = measurement_analysis(ROOT)
    assert (analysis["all_nuclear_state_rows"], analysis["rows_with_decay_modes"], analysis["decay_mode_entry_count"], analysis["distinct_decay_mode_code_count"], analysis["numeric_positive_half_life_row_count"]) == (5843, 5500, 8718, 50, 4700)
    assert analysis["all_codes_mapped"] is True
    assert analysis["literal_only_three_named_codes_rejected"] is True


def test_observational_provenance_and_no_fitted_extension_are_retained():
    assert len(RADIOACTIVE_DECAY_SPEC.axes) == 10
    assert RADIOACTIVE_DECAY_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    extension = next(axis for axis in RADIOACTIVE_DECAY_SPEC.axes if axis.key == "extension")
    assert extension.survivor.name == "no-extra-rule"
    source = (ROOT / "sft/physics/radioactive_decay_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("nubase", "4.463", "5.70", "6.0066", "source_path", "read_text"):
        assert forbidden not in source
