from fractions import Fraction

from sft.physics.relativistic_field_laws_v1 import (
    RELATIVISTIC_FIELD_SPECS,
    coulomb_gauss_closure,
    exact_optical_operations,
    finite_loop_sum,
    free_particle_phase,
    full_dirac_square,
    lorentz_transfer,
    magnetic_relativistic_factor,
    maxwell_closure,
    potential_phase_evolution,
    stationary_spectrum,
    two_hand_dirac_square,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_relativistic_and_field_arithmetic_is_exact():
    assert free_particle_phase(Fraction(1, 3), Fraction(1, 4))["phase_after"] == Fraction(5, 6)
    assert potential_phase_evolution(Fraction(1, 3), Fraction(1, 8), Fraction(1, 4))["phase_after"] == Fraction(17, 24)
    assert stationary_spectrum(2) == (Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8))
    assert two_hand_dirac_square() == {"momentum": Fraction(3, 5), "mass": Fraction(4, 5), "energy_square": Fraction(1, 1)}
    assert full_dirac_square()["direct_square"] == full_dirac_square()["polarized_square"] == 1
    assert full_dirac_square()["held_equal_differences"] == ((), ())
    assert coulomb_gauss_closure(Fraction(1, 8), Fraction(1, 4))["flux"] == Fraction(1, 8)
    assert magnetic_relativistic_factor(Fraction(1, 2))["electric_remainder"] == Fraction(3, 4)
    assert lorentz_transfer(Fraction(1, 4), Fraction(1, 2))["retained_force"] == Fraction(3, 16)
    assert maxwell_closure(2)["speed_square"] == maxwell_closure(3)["speed_square"] == 1
    assert exact_optical_operations()["dark_record"] == ()
    assert tuple(finite_loop_sum(k) for k in range(1, 7)) == (Fraction(1, 2), Fraction(3, 4), Fraction(7, 8), Fraction(15, 16), Fraction(31, 32), Fraction(63, 64))


def test_relativistic_field_specs_exhaust_registered_grammar():
    assert len(RELATIVISTIC_FIELD_SPECS) == 12
    for item in RELATIVISTIC_FIELD_SPECS:
        rows = candidate_rows(item)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(item) for row in rows) == 1
