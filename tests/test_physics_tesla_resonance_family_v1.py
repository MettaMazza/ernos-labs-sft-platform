from fractions import Fraction

from sft.physics.tesla_resonance_family_law_v1 import (
    SPECS,
    bounded_round_trip,
    complete_bounded_mode_prefix,
    common_recurrence_word,
    connected_path_reach,
    odd_quarter_count,
    orientation_inventory,
    quarter_boundary_roles,
    resonant_transfer_ledger,
)
from sft.physics.structural_constants import candidate_rows
from sft.physics.tesla_resonant_transfer_law_v2 import SPEC as TRANSFER_SPEC_V2


def test_all_four_formal_specs_exhaust_complete_grammar():
    assert len(SPECS) == 4
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256


def test_bounded_cavity_round_trip_modes_and_successor():
    assert bounded_round_trip(7) == 14
    assert complete_bounded_mode_prefix(3, 4) == (6, 12, 18, 24)
    assert bounded_round_trip(6) + 2 == bounded_round_trip(7)


def test_odd_quarter_family_is_generated_without_even_member():
    assert tuple(odd_quarter_count(n) for n in range(1, 6)) == (1, 3, 5, 7, 9)
    assert all(quarter_boundary_roles(n)[2] + 1 == n + n for n in range(1, 64))


def test_common_recurrence_retains_orientation_distinction():
    assert orientation_inventory() == {"longitudinal": 1, "transverse": 2, "complete": 3}
    assert common_recurrence_word(12)[:11] == common_recurrence_word(11)


def test_connected_resonant_transfer_preserves_complete_ledger():
    assert connected_path_reach(7) == (1, 2, 3, 4, 5, 6, 7)
    first = resonant_transfer_ledger(Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    second = resonant_transfer_ledger(Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    assert first["input"] == first["reconstructed"] == 1
    assert second["input"] == second["reconstructed"] == 1


def test_transfer_submission_uses_the_admitted_work_energy_identity():
    assert "SFT-PHYS-MECH-WORK-ENERGY-001" in TRANSFER_SPEC_V2.dependencies
    assert "SFT-PHYS-MECH-ENERGY-001" not in TRANSFER_SPEC_V2.dependencies
    assert len(candidate_rows(TRANSFER_SPEC_V2)) == 256


def test_invalid_native_inputs_halt():
    import pytest

    with pytest.raises(ValueError):
        bounded_round_trip(0)
    with pytest.raises(ValueError):
        resonant_transfer_ledger(Fraction(0, 1), Fraction(1, 2), Fraction(1, 2))
