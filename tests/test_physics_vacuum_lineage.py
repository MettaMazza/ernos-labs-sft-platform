from fractions import Fraction

from sft.physics.vacuum_lineage_laws_v1 import (
    VACUUM_LINEAGE_SPECS,
    asymmetric_vacuum_beat,
    complete_returned_cycle,
    odd_denominator_orbit,
    oscillator_levels,
    vacuum_floor,
    vacuum_inertia_exchange,
    vacuum_polarization_support,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_vacuum_exact_arithmetic_and_complete_ledgers():
    assert vacuum_floor() == Fraction(1, 2)
    assert oscillator_levels(2) == (
        Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8)
    )
    assert tuple(len(odd_denominator_orbit(d)) for d in (3, 5, 7, 9)) == (2, 4, 3, 6)
    assert vacuum_polarization_support() == (Fraction(1, 2), Fraction(1, 1))
    assert vacuum_inertia_exchange() == 1
    assert asymmetric_vacuum_beat() == {
        "vacuum_before": Fraction(1, 2),
        "vacuum_after": Fraction(1, 3),
        "local_work": Fraction(1, 6),
    }
    assert complete_returned_cycle()["restoration_cost"] == Fraction(1, 6)
    assert complete_returned_cycle()["restored_vacuum"] == Fraction(1, 2)
    assert complete_returned_cycle()["residual_work"] == ()


def test_vacuum_specs_have_complete_unique_censuses():
    assert len(VACUUM_LINEAGE_SPECS) == 6
    for spec in VACUUM_LINEAGE_SPECS:
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1
