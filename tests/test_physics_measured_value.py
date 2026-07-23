from fractions import Fraction
from pathlib import Path
import unittest

from sft.engine.fold_language import CapabilityClosedFoldInterpreter, FoldPair, PositiveRatio
from sft.physics.measured_value import (
    CODATA_SOURCE_HASH,
    CODATA_SOURCE_ID,
    CODATA_SOURCE_PATH,
    ExactMeasuredValueSpec,
    ExactRelationStep,
    MeasuredQuantity,
    exact_decimal,
    finite_decimal_prefix_interval,
    intervals_overlap,
    load_codata_interval,
    measured_value_program_document,
)
from sft.engine.fold_language import fold_program_from_mapping


ROOT = Path(__file__).resolve().parent.parent


def mass_energy_spec() -> ExactMeasuredValueSpec:
    return ExactMeasuredValueSpec(
        relation_id="mass-energy-square-speed",
        experiment_id="SFT-EXP-PHYS-MATTER-MASS-ENERGY-001",
        claim_id="SFT-PHYS-MATTER-MASS-ENERGY-001",
        relation_statement="The retained inertial carrier composed with two limiting-speed transfers predicts its energy carrier.",
        source_id=CODATA_SOURCE_ID,
        source_snapshot_path=CODATA_SOURCE_PATH,
        source_snapshot_hash=CODATA_SOURCE_HASH,
        inputs=(
            MeasuredQuantity("mass", "electron mass", "kg"),
            MeasuredQuantity("speed", "speed of light in vacuum", "m s^-1"),
        ),
        steps=(
            ExactRelationStep("speed_square", "product", "speed", "speed"),
            ExactRelationStep("energy", "product", "mass", "speed_square"),
        ),
        output_key="energy",
        target=MeasuredQuantity("target_energy", "electron mass energy equivalent", "J"),
        falsification_condition="The exact predicted and external measurement intervals do not overlap.",
    )


class ExactMeasuredValueTests(unittest.TestCase):
    def test_decimal_parser_is_exact_and_rejects_nonfinite_or_signed_records(self):
        self.assertEqual(exact_decimal("1.25 e-3"), Fraction(1, 800))
        self.assertEqual(exact_decimal("299 792 458"), Fraction(299792458, 1))
        for invalid in ("0", "-1.2", "1.23... e-4", ""):
            with self.assertRaises(ValueError):
                exact_decimal(invalid)
        lower, upper = finite_decimal_prefix_interval("2.083 661 912... e10")
        self.assertEqual(upper - lower, Fraction(10, 1))

    def test_codata_loader_preserves_exact_interval(self):
        row = load_codata_interval(ROOT / CODATA_SOURCE_PATH, MeasuredQuantity("mass", "electron mass", "kg"))
        self.assertLess(row.lower, row.central)
        self.assertLess(row.central, row.upper)
        exact = load_codata_interval(ROOT / CODATA_SOURCE_PATH, MeasuredQuantity("speed", "speed of light in vacuum", "m s^-1"))
        self.assertEqual(exact.lower, exact.upper)

    def test_compiled_relation_predicts_external_mass_energy_interval(self):
        spec = mass_energy_spec()
        rows = {item.key: load_codata_interval(ROOT / CODATA_SOURCE_PATH, item) for item in spec.inputs}
        inputs = {
            key: PositiveRatio.from_pair(value.numerator, value.denominator)
            for item in spec.inputs
            for key, value in (
                (item.key + "__lower", rows[item.key].lower),
                (item.key + "__upper", rows[item.key].upper),
            )
        }
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(measured_value_program_document(spec)), inputs
        )
        target = load_codata_interval(ROOT / CODATA_SOURCE_PATH, spec.target).fold_pair()
        self.assertTrue(intervals_overlap(execution.output, target))
        self.assertIsInstance(execution.output, FoldPair)

    def test_displaced_interval_is_rejected(self):
        predicted = FoldPair(PositiveRatio.from_pair(3, 2), PositiveRatio.from_pair(5, 2))
        displaced = FoldPair(PositiveRatio.from_pair(7, 2), PositiveRatio.from_pair(9, 2))
        self.assertFalse(intervals_overlap(predicted, displaced))


if __name__ == "__main__":
    unittest.main()
