from fractions import Fraction

from sft.physics.atomic_constants import inverse_fine_structure
from sft.physics.matter_flavour_terminal_ckm_laws_v1 import (
    TERMINAL_SPECS,
    terminal_baryon_photon_relation,
    terminal_ckm_relation,
    terminal_ckm_slope_contribution,
)


def test_terminal_ckm_dependency_is_transport_complete():
    assert len(TERMINAL_SPECS) == 2
    assert terminal_ckm_slope_contribution() == Fraction(1, 1) / (3 * (inverse_fine_structure() + 7))
    assert terminal_ckm_relation()["phase"] == Fraction(1, 2)
    assert terminal_baryon_photon_relation()["imbalance_share"] == Fraction(1, 2)


def test_terminal_specs_disclose_observational_provenance():
    for spec in TERMINAL_SPECS:
        assert tuple(row.value for row in spec.provenance) == ("observational_derivation",)
        assert len(spec.axes) == 8
