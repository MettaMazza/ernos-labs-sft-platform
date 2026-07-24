from fractions import Fraction

from sft.physics.matter_flavour_completion_laws_v1 import (
    COMPLETION_SPECS,
    confinement_lift,
    generation_depth,
    inter_entry_couplings,
    mass_ratio_family,
    mirror_mass_closure,
    mixing_correspondence,
    sharpened_quark_products,
)


def test_omitted_matter_flavour_chain_closes_exactly():
    assert len(COMPLETION_SPECS) == 7
    assert mixing_correspondence()["lepton_matrix"][0] == (Fraction(5, 6), Fraction(1, 2), Fraction(1, 6))
    assert tuple(mass_ratio_family(depth)["heavy_over_light"] for depth in (1, 2, 3)) == (5, 17, 53)
    assert mirror_mass_closure()["mirror_closed"] is True
    assert inter_entry_couplings()["quark_lock"] == Fraction(2, 3)
    assert inter_entry_couplings()["lepton_lock"] == Fraction(1, 2)
    assert generation_depth()["generator_steps"] == 2
    assert sharpened_quark_products() == {"down": Fraction(3, 1454), "up": Fraction(3, 13118)}
    assert confinement_lift()["lightest_carrier_lift"] == 2


def test_every_completion_spec_has_one_survivor_shape():
    for spec in COMPLETION_SPECS:
        assert len(spec.axes) == 8
        assert all(axis.survivor.reason for axis in spec.axes)
