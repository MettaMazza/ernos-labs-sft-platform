from fractions import Fraction

import pytest

from sft.physics.structural_constants import candidate_rows
from sft.physics.vacuum_inertia_drive_family_law_v1 import (
    SPECS,
    bounded_driven_carrier,
    complete_drive_response_ledger,
    covariation_record,
    finite_depth_floor,
    live_phase_trace,
    local_resonant_drive,
)


def test_complete_formal_family_grammar():
    assert len(SPECS) == 4
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256


def test_local_drive_and_live_phase():
    record = local_resonant_drive(Fraction(1, 3), Fraction(1, 4))
    assert record["transferred"] == Fraction(1, 12)
    assert record["reconstructed"] == record["source"]
    assert live_phase_trace(Fraction(1, 3), 2) == (Fraction(2, 3), Fraction(1, 3))


def test_unity_forces_equal_covariation():
    record = covariation_record(Fraction(1, 3), Fraction(1, 4))
    assert record["vacuum_change"] == record["inertia_change"] == Fraction(1, 12)
    assert record["initial_ratio"] == record["driven_ratio"] == 1


def test_finite_depth_floor_remains_positive():
    assert tuple(finite_depth_floor(depth) for depth in range(1, 4)) == (
        Fraction(1, 4), Fraction(1, 8), Fraction(1, 16)
    )
    assert bounded_driven_carrier(Fraction(1, 4), 3) == Fraction(1, 4)
    with pytest.raises(ValueError):
        bounded_driven_carrier(Fraction(1, 32), 3)


def test_complete_ledger_restores_both_carriers_and_retains_six_stages():
    record = complete_drive_response_ledger(Fraction(1, 3), Fraction(1, 4))
    assert record["closed"]
    assert record["outward_transfer"] == record["restoration_transfer"] == Fraction(1, 12)
    assert len(record["information_record"]) == 6
