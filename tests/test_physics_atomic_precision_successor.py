from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.atomic_precision_successor_laws_v1 import (
    ATOMIC_PRECISION_SPECS,
    depth_three_heavy_complement,
    predecessor_up_support,
    reduced_mass_retention,
    terminal_binary_support,
    terminal_fine_carrier,
    terminal_hyperfine_carrier_interval,
    terminal_lamb_carrier,
    terminal_proton_magnetic_projection,
    terminal_proton_ratio_interval,
)
from sft.physics.atomic_precision_successor_validation_v1 import (
    FINE_LABEL,
    HYPERFINE_LABEL,
    LAMB_LABEL,
    atomic_precision_classification,
    target_interval,
    translated_prediction_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_atomic_precision_carriers_are_exact_and_structurally_closed():
    assert depth_three_heavy_complement() == 53
    assert predecessor_up_support() == 64
    assert terminal_binary_support() == 16
    assert Fraction(1, 10 ** 7) < terminal_lamb_carrier() < Fraction(1, 10 ** 6)
    assert Fraction(1, 10 ** 6) < terminal_fine_carrier() < Fraction(1, 100000)


def test_terminal_hyperfine_retains_exact_algebraic_mass_and_reduced_mass():
    proton = terminal_proton_ratio_interval()
    assert Fraction(1800, 1) < proton[0] < proton[1] < Fraction(1900, 1)
    assert Fraction(9, 10) < reduced_mass_retention(proton[0]) < Fraction(1, 1)
    assert Fraction(2, 1) < terminal_proton_magnetic_projection() < Fraction(3, 1)
    hyperfine = terminal_hyperfine_carrier_interval()
    assert Fraction(1, 10 ** 7) < hyperfine[0] < hyperfine[1] < Fraction(1, 10 ** 6)


def test_atomic_precision_postseal_NIST_intervals_pass_exactly():
    expected = {"lamb": LAMB_LABEL, "fine": FINE_LABEL, "hyperfine": HYPERFINE_LABEL}
    for kind, label in expected.items():
        prediction = translated_prediction_interval(ROOT, kind)
        target = target_interval(ROOT, kind)
        assert prediction[0] < prediction[1]
        assert target[0] < target[1]
        assert atomic_precision_classification(ROOT, kind) == label


def test_atomic_precision_grammars_and_provenance_are_complete():
    assert all(len(spec.axes) == 10 for spec in ATOMIC_PRECISION_SPECS)
    assert all(spec.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,) for spec in ATOMIC_PRECISION_SPECS)


def test_atomic_precision_formal_module_contains_no_measurement_target_or_source_access():
    source = (ROOT / "sft/physics/atomic_precision_successor_laws_v1.py").read_text(encoding="utf-8")
    for forbidden in (
        "1057829800",
        "10969029800",
        "1420405751",
        "3289841960250000",
        "nist",
        "read_text",
        "SOURCE_PATH",
    ):
        assert forbidden.lower() not in source.lower()
