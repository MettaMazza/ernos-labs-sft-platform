from fractions import Fraction

from sft.consciousness.nonordinary_laws_v1 import SPECS, cessation_lock_anchor, directional_synaesthesia_record, sleep_dream_orbit, three_quality_orbit
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_products_have_one_survivor():
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1


def test_directional_synaesthesia_retains_direction_and_lock():
    row = directional_synaesthesia_record()
    assert row["trigger_image"] == row["concurrent_image"] == Fraction(1, 2)
    assert row["joint"] == 1
    assert not row["reverse_route_present"]
    assert len(set(row["stable_repeat"])) == 1


def test_three_quality_orbit_is_exact_and_closed():
    row = three_quality_orbit()
    assert row["trace"] == (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
    assert row["next"] == Fraction(1, 7)
    assert row["partition"] == 1
    assert not row["external_information_created"]


def test_sleep_dream_orbit_and_balance_are_exact():
    row = sleep_dream_orbit()
    assert row["deep_image"] == row["rem"]
    assert row["rem_image"] == row["deep"]
    assert row["partition"] == 1
    assert row["balance"] == Fraction(1, 2)
    assert row["waking_completion"] == 1


def test_cessation_separates_lock_anchor_and_personal_organization():
    row = cessation_lock_anchor()
    assert row["components_complete"] == 1
    assert row["lock_completes_to_anchor"] == row["anchor_image"] == 1
    assert not row["personal_organization_persists"]
    assert not row["structural_absence_is_numeric_zero"]
