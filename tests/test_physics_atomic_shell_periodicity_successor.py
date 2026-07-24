from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.atomic_shell_periodicity_successor_laws_v1 import (
    ATOMIC_SHELL_PERIODICITY_SPEC,
    generated_period_closures,
    generated_period_widths,
    shell_capacity,
)
from sft.physics.atomic_shell_periodicity_successor_validation_v1 import (
    MEASURED_LABEL,
    atomic_periodicity_classification,
    ionization_interval,
)


ROOT = Path(__file__).resolve().parents[1]


def test_shell_sum_is_exact_and_depth_independent():
    assert all(shell_capacity(rank) == 2 * rank * rank for rank in range(1, 65))
    assert tuple(shell_capacity(rank) for rank in range(1, 5)) == (2, 8, 18, 32)


def test_generated_closures_and_period_widths_are_distinguished():
    assert generated_period_closures(7) == (2, 10, 18, 36, 54, 86, 118)
    assert generated_period_widths(7) == (2, 8, 8, 18, 18, 32, 32)


def test_complete_postseal_periodicity_vector_passes_exactly():
    assert atomic_periodicity_classification(ROOT) == MEASURED_LABEL
    for endpoint, successor in (("He", "Li"), ("Ne", "Na"), ("Ar", "K"), ("Kr", "Rb"), ("Xe", "Cs"), ("Rn", "Fr")):
        assert ionization_interval(ROOT, endpoint)[0] > ionization_interval(ROOT, successor)[1]


def test_local_ionization_dips_are_retained_not_erased():
    for first, second in (("Be", "B"), ("N", "O"), ("Mg", "Al")):
        assert ionization_interval(ROOT, first)[0] > ionization_interval(ROOT, second)[1]


def test_atomic_periodicity_grammar_provenance_and_target_boundary():
    assert len(ATOMIC_SHELL_PERIODICITY_SPEC.axes) == 10
    assert ATOMIC_SHELL_PERIODICITY_SPEC.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
    source = (ROOT / "sft/physics/atomic_shell_periodicity_successor_laws_v1.py").read_text(encoding="utf-8").lower()
    for forbidden in ("nist", "iupac", "24.587", "21.564", "read_text", "source_path"):
        assert forbidden not in source
