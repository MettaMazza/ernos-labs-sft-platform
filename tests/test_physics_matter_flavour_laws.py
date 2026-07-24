from fractions import Fraction

from sft.physics.matter_flavour_laws_v1 import (
    MATTER_FLAVOUR_SPECS,
    ckm_fibres,
    majorana_structure,
    magnetic_anomaly_structure,
    neutrino_mass_squares,
    neutrino_splitting_structure,
    pmns_cp_structure,
    quark_channel_invariants,
    quark_cubic_invariants,
    quark_dressing_factors,
    quark_root_brackets,
    zero_nu_noncancellation,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_matter_flavour_exact_results():
    assert quark_channel_invariants() == {"up_pair_sum": Fraction(1, 12), "down_pair_sum": Fraction(1, 8), "up_depth": 7, "down_depth": 5}
    assert quark_cubic_invariants()["down"] == (Fraction(1, 1), Fraction(1, 8), Fraction(1, 383))
    assert quark_cubic_invariants()["up"] == (Fraction(1, 1), Fraction(1, 12), Fraction(1, 3071))
    assert all(len(rows) == 3 for rows in quark_root_brackets().values())
    assert quark_dressing_factors()["central_down_lift"] > 1
    assert 0 < quark_dressing_factors()["upper_up_retention"] < 1
    assert ckm_fibres()["matrix"][0] == (Fraction(8, 9), Fraction(5, 9), Fraction(2, 9))
    assert neutrino_splitting_structure()["rung_ratio"] == 33
    assert neutrino_splitting_structure()["translation_ratio"] == Fraction(3, 100)
    assert neutrino_mass_squares() == {"lightest": Fraction(1, 32), "middle": Fraction(33, 32), "heavy": Fraction(3203, 96)}
    assert pmns_cp_structure()["electron_weights"] == (Fraction(47, 72), Fraction(47, 144), Fraction(1, 48))
    assert majorana_structure()["self_antipodal_lock"] is True
    assert majorana_structure()["generic_hand_self_antipodal"] is False
    assert zero_nu_noncancellation()["positive_floor_coefficient"] > 0
    assert magnetic_anomaly_structure()["bare_g"] == 2


def test_matter_flavour_complete_candidate_products():
    assert len(MATTER_FLAVOUR_SPECS) == 12
    for item in MATTER_FLAVOUR_SPECS:
        rows = candidate_rows(item)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(item) for row in rows) == 1
