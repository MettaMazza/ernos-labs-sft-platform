from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.structural_constants import candidate_rows
from sft.physics.thermal_history_recombination_terminal_law_v1 import (
    SPEC,
    acoustic_mode_ledger,
    finite_sound_horizon,
    freezeout_capture_ledger,
    live_depth_seven_orbit,
    ordered_thresholds,
    temperature_scale_invariant,
    transported_temperature,
    visibility_ledger,
)


class ThermalHistoryRecombinationTerminalTests(unittest.TestCase):
    def test_temperature_scale_transport_is_exact(self) -> None:
        self.assertEqual(transported_temperature(Fraction(3, 4), Fraction(3, 2)), Fraction(1, 2))
        self.assertTrue(temperature_scale_invariant(Fraction(3, 4), Fraction(3, 2)))
        self.assertEqual(
            ordered_thresholds((Fraction(1, 4), Fraction(7, 8), Fraction(1, 2))),
            (Fraction(7, 8), Fraction(1, 2), Fraction(1, 4)),
        )

    def test_freezeout_and_capture_types_are_not_conflated(self) -> None:
        self.assertEqual(live_depth_seven_orbit(), (1, 2, 4))
        row = freezeout_capture_ledger()
        self.assertEqual(row["freezeout_neutron_share"], Fraction(1, 7))
        self.assertEqual(row["freezeout_neutron_proton_ratio"], Fraction(1, 6))
        self.assertEqual(row["capture_neutron_share"], Fraction(1, 8))
        self.assertEqual(row["capture_neutron_proton_ratio"], Fraction(1, 7))
        self.assertEqual(row["helium_family_mass_share"], Fraction(1, 4))
        self.assertEqual(row["hydrogen_family_mass_share"], Fraction(3, 4))

    def test_visibility_is_finite_positive_and_uniquely_centred(self) -> None:
        for radius in range(1, 12):
            row = visibility_ledger(radius)
            self.assertTrue(row["complete"])
            self.assertTrue(row["unique_midpoint"])
            self.assertTrue(all(value > 0 for value in row["normalized"]))

    def test_acoustic_modes_retain_internal_parity(self) -> None:
        rows = acoustic_mode_ledger(6)
        self.assertEqual(tuple(row["mode"] for row in rows), (1, 2, 3, 4, 5, 6))
        self.assertEqual(
            tuple(row["loading"] for row in rows),
            ("compression", "rarefaction", "compression", "rarefaction", "compression", "rarefaction"),
        )
        self.assertEqual(
            finite_sound_horizon((Fraction(1, 4), Fraction(1, 2)), (Fraction(2, 3), Fraction(3, 4))),
            Fraction(13, 24),
        )

    def test_invalid_inputs_halt(self) -> None:
        for value in (Fraction(0), Fraction(-1)):
            with self.assertRaises(ValueError):
                transported_temperature(Fraction(1), value)
            with self.assertRaises(ValueError):
                transported_temperature(value, Fraction(1))
        with self.assertRaises(ValueError):
            ordered_thresholds(())
        with self.assertRaises(ValueError):
            ordered_thresholds((Fraction(1, 2), Fraction(1, 2)))
        with self.assertRaises(ValueError):
            visibility_ledger(0)
        with self.assertRaises(ValueError):
            acoustic_mode_ledger(-1)
        with self.assertRaises(ValueError):
            finite_sound_horizon((Fraction(1, 2),), (Fraction(1, 2), Fraction(1, 3)))

    def test_complete_engine_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
