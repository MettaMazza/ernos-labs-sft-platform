from fractions import Fraction
from sft.astronomy.prior_return_laws_v1 import SPECS, atomic_burst, lithium_depletion, planetary_ladder, tipping_lock, unit_release
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_products_have_one_survivor():
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert sum(r["candidate_id"] == survivor_id(spec) for r in rows) == 1


def test_tipping_lock():
    r = tipping_lock(); assert r["images"] == (Fraction(1, 2), Fraction(1, 2)); assert r["partition"] == 1


def test_unit_release():
    r = unit_release(); assert len(r["rows"]) == 10; assert r["all_products_one"]; assert r["exponent"] == 1


def test_atomic_burst():
    r = atomic_burst(); assert r["completion"] == 1; assert r["steps"] == 1; assert not r["intermediate_generated"]


def test_planetary_ladder():
    r = planetary_ladder(); assert r["values"][0] == Fraction(1, 128); assert r["terminal"] == 1; assert set(r["ratios"]) == {2}


def test_lithium_depletion():
    r = lithium_depletion(); assert r["prior"] == Fraction(3, 16); assert r["surface"] == Fraction(3, 32); assert r["restored"] == r["prior"]
