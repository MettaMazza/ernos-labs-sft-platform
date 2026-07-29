from fractions import Fraction

from sft.biology.prior_mechanisms_laws_v1 import (
    SPECS,
    autocatalytic_ignition,
    cancer_mechanism_record,
    ecosystem_orbit,
    homochiral_amplification,
    neural_threshold_record,
    transient_to_odd_recurrence,
)


def test_all_specs_have_complete_unique_products():
    from sft.physics.structural_constants import candidate_rows, survivor_id
    for row in SPECS.values():
        assert len(candidate_rows(row)) == 256
        assert sum(item["candidate_id"] == survivor_id(row) for item in candidate_rows(row)) == 1


def test_autocatalytic_boundary_is_least_one_act_closure():
    for roles in range(2, 18):
        row = autocatalytic_ignition(roles)
        assert row["internally_supported_before_seed"] + 1 == roles
        assert all(supported + 1 < roles for supported in row["below_boundary_supported_counts"])


def test_homochiral_amplification_is_exact_monotone_and_finite():
    rows = tuple(homochiral_amplification(depth) for depth in range(1, 17))
    assert all(right["selected_share"] > left["selected_share"] for left, right in zip(rows, rows[1:]))
    assert all(row["opposed_count"] == 1 and row["selected_share"] < 1 for row in rows)


def test_somatic_transient_count_equals_two_power_count():
    for power in range(1, 9):
        for odd in range(3, 18, 2):
            row = transient_to_odd_recurrence(power, odd)
            assert row["transient_count"] == power
            assert row["recurrent_entry"] == Fraction(1, odd)
            assert row["odd_recurrent_orbit"][-1] == Fraction(1, odd)


def test_half_one_event_and_subthreshold_absence_are_distinct():
    row = neural_threshold_record()
    assert row["least_activation"] == Fraction(1, 2)
    assert row["completion"] == 1
    assert row["below_double"] < 1
    assert row["event_output"] != row["below_output"] != row["refractory_record"]


def test_cancer_mechanism_requires_complete_conjunction():
    row = cancer_mechanism_record()
    assert row["persistent_nonterminal_cycle"]
    assert row["required_differentiation_transition"] == "structurally-absent"
    assert row["division_death_differentiation_control_escape"]
    assert not row["cycling_alone_sufficient"]


def test_ecosystem_orbit_is_exact_period_four():
    assert ecosystem_orbit() == (Fraction(3, 5), Fraction(1, 5), Fraction(2, 5), Fraction(4, 5), Fraction(3, 5))


def test_registered_biology_sources_remain_intact(tmp_path):
    from pathlib import Path
    from sft.biology.prior_mechanisms_external_v1 import _source_derived_target, PREDICTION_LABEL
    root = Path(__file__).resolve().parents[1]
    observed, extraction_hash, source_ids = _source_derived_target(root)
    assert observed == PREDICTION_LABEL
    assert extraction_hash.startswith("sha256:")
    assert len(source_ids) == 7
