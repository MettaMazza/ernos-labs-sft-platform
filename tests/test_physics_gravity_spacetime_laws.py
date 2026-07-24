from fractions import Fraction

from sft.physics.gravity_spacetime_laws_v1 import (
    GRAVITY_SPACETIME_SPECS,
    closed_timelike_admissible,
    exact_clock_rate,
    exact_interval,
    finite_distance_floor,
    gravitational_wave_trace,
    graviton_polarizations,
    horizon_information_ledger,
    interval_witness,
    lattice_laplacian,
    nonlinear_gravity,
    redshift_equivalence,
    square_lattice_curvature,
    static_clock,
    strong_field_horizon,
    warp_admissible,
    weak_gravity,
    wormhole_admissible,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_gravity_spacetime_exact_results_and_boundaries():
    assert weak_gravity(Fraction(1, 8), Fraction(1, 4))["flux"] == Fraction(1, 8)
    assert interval_witness()["proper_time"] == Fraction(4, 5)
    assert exact_interval(Fraction(1, 1), Fraction(1, 1))["interval_square"] == ()
    assert static_clock(Fraction(1, 8))["folded_metric"] == Fraction(3, 4)
    assert exact_clock_rate() == Fraction(3, 4)
    assert redshift_equivalence(Fraction(1, 4), Fraction(1, 1))["gravitational_redshift"] == Fraction(1, 4)
    assert square_lattice_curvature(Fraction(1, 2), Fraction(1, 8)) == 2
    assert tuple(lattice_laplacian(d, Fraction(1, 8)) for d in (1, 2, 3)) == (2, 4, 6)
    assert nonlinear_gravity()["self_source_correction"] == Fraction(1, 72)
    assert graviton_polarizations(4)["physical_polarizations"] == 2
    assert graviton_polarizations(3)["physical_polarizations"] == ()
    assert gravitational_wave_trace()["first_unfrozen_second_differences"] == (12, 18)
    assert strong_field_horizon()["entropy_cells"] == 8
    assert all(finite_distance_floor(k) > 0 for k in range(1, 17))
    assert len(horizon_information_ledger()["retained_boundary_records"]) == 8
    assert wormhole_admissible(Fraction(1, 4), True, True)
    assert not wormhole_admissible(Fraction(1, 4), False, True)
    assert warp_admissible(Fraction(1, 4), Fraction(1, 4), True)
    assert not warp_admissible(Fraction(1, 4), Fraction(1, 2), True)
    assert closed_timelike_admissible(("state", "proof"), ("state", "proof"), True)
    assert not closed_timelike_admissible(("state", "proof"), ("changed", "proof"), True)


def test_gravity_spacetime_complete_candidate_products():
    assert len(GRAVITY_SPACETIME_SPECS) == 13
    for item in GRAVITY_SPACETIME_SPECS:
        rows = candidate_rows(item)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(item) for row in rows) == 1
