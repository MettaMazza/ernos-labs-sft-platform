from fractions import Fraction
from pathlib import Path

from sft.physics.atomic_spectra_postseal_validation_v1 import (
    CUBIC_SPEC,
    HYDROGEN_SPEC,
    cubic_observed_coordination,
    hydrogen_comparison,
    source_record,
)
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_complete_source_custody_and_unfavorable_molecular_row_are_retained():
    record = source_record(ROOT)
    assert len(record["sources"]) == 4
    assert record["custody"]["development_targets_already_known"] is True
    assert record["custody"]["target_inaccessible_during_prediction_execution"] is True
    assert record["custody"]["unfavorable_molecular_ratio_retained"] is True


def test_cubic_comparison_is_exact_and_complete():
    assert cubic_observed_coordination(ROOT) == 6
    assert len(candidate_rows(CUBIC_SPEC)) == 256
    assert survivor_id(CUBIC_SPEC).count("__") == 7


def test_hydrogen_predictions_use_sealed_ratios_and_full_exact_intervals():
    comparison = hydrogen_comparison(ROOT)
    assert comparison["lyman_prediction"] == Fraction(3290363151, 40000)
    assert comparison["balmer_prediction"] == Fraction(1096787717, 72000)
    assert comparison["lyman_lower"] == Fraction(4112951, 50)
    assert comparison["lyman_upper"] == Fraction(822593, 10)
    assert comparison["balmer_lower"] == Fraction(761657, 50)
    assert comparison["balmer_upper"] == Fraction(380832, 25)
    assert comparison["lyman_passed"] is True
    assert comparison["balmer_passed"] is True
    assert len(candidate_rows(HYDROGEN_SPEC)) == 256


def test_formal_atomic_source_remains_measurement_free():
    source = (ROOT / "sft/physics/atomic_spectra_completion_laws_v1.py").read_text(encoding="utf-8")
    for target in ("109678.7717", "82259.16", "15233.21", "91700.0", "4401.213", "60.8530"):
        assert target not in source
