from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.nucleon_binding_successor_laws_v1 import (
    NUCLEON_BINDING_SPEC,
    colour_cycle,
    neutron_proton_order_certificate,
    nucleon_flavour_words,
    nucleon_mass_ledger,
)
from sft.physics.nucleon_binding_successor_validation_v1 import (
    MEASURED_LABEL,
    nucleon_binding_classification,
    uud_current_mass_fraction_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_colour_cycle_and_nucleon_words_close_exactly():
    assert colour_cycle() == (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
    assert nucleon_flavour_words() == {"proton": ("up", "up", "down"), "neutron": ("up", "down", "down")}


def test_depth_seven_mass_ledger_forces_binding_dominance():
    ledger = nucleon_mass_ledger()
    assert ledger == {"depth": 7, "support": 128, "bare": Fraction(1, 128), "held_cycle": Fraction(127, 128)}
    assert ledger["bare"] < Fraction(1, 100)
    assert ledger["held_cycle"] > Fraction(99, 100)


def test_exact_flavour_surplus_exceeds_admitted_proton_dressing():
    certificate = neutron_proton_order_certificate()
    assert certificate["flavour_surplus_lower"] > certificate["proton_electromagnetic_dressing"]
    assert certificate["net_neutron_surplus_lower"] > Fraction(1, 1000)


def test_complete_postseal_PDG_NIST_vector_passes_with_nonconflation():
    assert nucleon_binding_classification(ROOT) == MEASURED_LABEL
    current = uud_current_mass_fraction_interval(ROOT)
    assert current[1] < Fraction(1, 100)
    assert not current[0] <= Fraction(1, 128) <= current[1]


def test_observational_provenance_and_formal_target_boundary_are_retained():
    assert len(NUCLEON_BINDING_SPEC.axes) == 12
    assert NUCLEON_BINDING_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    source = (ROOT / "sft/physics/nucleon_binding_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("938.272", "939.565", "2.20", "4.69", "read_text", "source_path"):
        assert forbidden not in source
