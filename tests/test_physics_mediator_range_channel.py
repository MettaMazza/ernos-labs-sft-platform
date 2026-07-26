from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.mediator_range_channel_terminal_law_v1 import (
    EMPTY_ONE,
    SPEC,
    broken_channel_mass,
    finite_reach_count,
    larger_mass_shorter_range,
    ledger_conserves_one,
    massless_forward_trace,
    preserved_mass_record,
)


class MediatorRangeChannelTests(unittest.TestCase):
    def test_preserved_and_broken_channels(self) -> None:
        self.assertEqual(preserved_mass_record(Fraction(1, 1)), EMPTY_ONE)
        self.assertEqual(broken_channel_mass(Fraction(2, 3)), Fraction(1, 3))

    def test_v2_reach_examples(self) -> None:
        self.assertEqual(finite_reach_count(Fraction(1, 3)), 2)
        self.assertEqual(finite_reach_count(Fraction(1, 7)), 6)

    def test_conservation_and_order(self) -> None:
        self.assertTrue(ledger_conserves_one(Fraction(1, 3)))
        self.assertTrue(larger_mass_shorter_range(Fraction(1, 7), Fraction(1, 3)))

    def test_massless_trace(self) -> None:
        self.assertEqual(massless_forward_trace(8), (Fraction(1, 1),) * 9)

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)


if __name__ == "__main__":
    unittest.main()
