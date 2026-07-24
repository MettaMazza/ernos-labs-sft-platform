from fractions import Fraction
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.hydrogen_rydberg_successor_laws_v1 import (
    HYDROGEN_RYDBERG_SPEC,
    terminal_hydrogen_scale_interval,
    terminal_ionization_to_electron_rest_interval,
    terminal_line_ratio_interval,
)
from sft.physics.hydrogen_rydberg_successor_validation_v1 import (
    MEASURED_LABEL,
    hydrogen_rydberg_classification,
    ionization_target_interval,
    line_target_interval,
    predicted_ionization_interval,
    predicted_line_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_terminal_hydrogen_scale_is_exact_and_strict():
    scale = terminal_hydrogen_scale_interval()
    rest = terminal_ionization_to_electron_rest_interval()
    assert Fraction(99, 100) < scale[0] < scale[1] < Fraction(1, 1)
    assert Fraction(1, 100000) < rest[0] < rest[1] < Fraction(1, 10000)


def test_terminal_hydrogen_line_ratios_preserve_the_exact_ladder():
    lyman = terminal_line_ratio_interval(Fraction(3, 4))
    balmer = terminal_line_ratio_interval(Fraction(5, 36))
    assert lyman[0] > balmer[1] > 0


def test_terminal_hydrogen_postseal_NIST_vector_passes_exactly():
    ionization = predicted_ionization_interval(ROOT)
    target = ionization_target_interval(ROOT)
    assert target[0] <= ionization[0] <= ionization[1] <= target[1]
    for kind, gap in (("lyman_alpha", Fraction(3, 4)), ("balmer_alpha", Fraction(5, 36))):
        prediction = predicted_line_interval(ROOT, gap)
        line = line_target_interval(ROOT, kind)
        assert prediction[0] <= line[1] and line[0] <= prediction[1]
    assert hydrogen_rydberg_classification(ROOT) == MEASURED_LABEL


def test_terminal_hydrogen_grammar_and_provenance_are_complete():
    assert len(HYDROGEN_RYDBERG_SPEC.axes) == 10
    assert HYDROGEN_RYDBERG_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)


def test_terminal_hydrogen_formal_module_contains_no_measurement_or_source_access():
    source = (ROOT / "sft/physics/hydrogen_rydberg_successor_laws_v1.py").read_text(encoding="utf-8")
    for forbidden in (
        "109737.315",
        "109678.7717",
        "82259.16",
        "15233.21",
        "nist",
        "read_text",
        "SOURCE_PATH",
    ):
        assert forbidden.lower() not in source.lower()
