from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.cosmic_component_transport_terminal_law_v1 import (
    SPEC,
    acceleration_onset_cube,
    component_laws,
    late_squared_expansion,
    matter_fraction,
    matter_transport,
    matter_vacuum_equality_cube,
    present_acceleration_magnitude,
    radiation_transport,
    vacuum_fraction,
    vacuum_transport,
)
from sft.physics.cosmic_component_transport_terminal_validation_v1 import cosmic_transport_measurement_record
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class CosmicComponentTransportTerminalTests(unittest.TestCase):
    def test_component_transport_is_exact(self) -> None:
        self.assertEqual(matter_transport(Fraction(3, 2)), Fraction(27, 8))
        self.assertEqual(radiation_transport(Fraction(3, 2)), Fraction(81, 16))
        self.assertEqual(vacuum_transport(Fraction(3, 2)), Fraction(1))
        self.assertEqual(tuple(row["transport_power"] for row in component_laws()[:2]), (3, 4))

    def test_terminal_curve_replaces_old_budget(self) -> None:
        self.assertEqual(late_squared_expansion(Fraction(1)), Fraction(1))
        self.assertEqual(late_squared_expansion(Fraction(2)), Fraction(51, 16))
        self.assertEqual(late_squared_expansion(Fraction(3)), Fraction(73, 8))
        self.assertEqual(matter_fraction(Fraction(1)), Fraction(5, 16))
        self.assertEqual(matter_fraction(Fraction(2)), Fraction(40, 51))
        self.assertEqual(matter_fraction(Fraction(3)), Fraction(135, 146))
        self.assertTrue(all(matter_fraction(r) + vacuum_fraction(r) == 1 for r in (Fraction(1), Fraction(2), Fraction(3))))

    def test_thresholds_and_typed_acceleration(self) -> None:
        self.assertEqual(matter_vacuum_equality_cube(), Fraction(11, 5))
        self.assertEqual(acceleration_onset_cube(), Fraction(22, 5))
        self.assertEqual(present_acceleration_magnitude(), Fraction(17, 32))
        self.assertEqual(component_laws()[2]["pressure_orientation"], "tension-One")

    def test_invalid_stretch_halts(self) -> None:
        for invalid in (Fraction(0), Fraction(-1), Fraction(-3, 2)):
            with self.assertRaises(ValueError):
                late_squared_expansion(invalid)

    def test_complete_external_vector(self) -> None:
        record = cosmic_transport_measurement_record(ROOT)
        self.assertEqual(len(record["chronometer_rows"]), 32)
        self.assertTrue(record["all_thirty_two_chronometers_pass"])
        self.assertTrue(record["equality_passed"])
        self.assertTrue(record["planck_onset_passed"])
        self.assertTrue(record["q_magnitude_passed"])
        self.assertTrue(record["transition_passed"])
        self.assertTrue(record["vacuum_tension_passed"])
        self.assertTrue(record["desi_adverse_row_retained"])

    def test_complete_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
