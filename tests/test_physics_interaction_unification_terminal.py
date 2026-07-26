from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.interaction_unification_terminal_law_v1 import (
    SPEC,
    all_depth_order_and_noncoincidence,
    base_sector_table,
    common_half_one_sectors,
    period_dictionary,
    prior_flat_slope_bundle_is_consistent,
)


class InteractionUnificationTerminalTests(unittest.TestCase):
    def test_sector_table(self) -> None:
        self.assertEqual(base_sector_table(2)["coupling"], Fraction(1, 2))
        self.assertEqual(base_sector_table(3)["mediator_count"], 8)
        self.assertEqual(base_sector_table(7)["mass_shortfall"], Fraction(1, 7))

    def test_shared_half_and_periods(self) -> None:
        self.assertEqual(common_half_one_sectors(), (3, 5, 7))
        self.assertEqual(period_dictionary(), {"gravity": 1, "electromagnetic": 2, "strong": 3, "joint": 6})

    def test_order_and_adverse_bundle(self) -> None:
        self.assertTrue(all(all_depth_order_and_noncoincidence(depth) for depth in range(1, 18)))
        self.assertFalse(prior_flat_slope_bundle_is_consistent())

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)


if __name__ == "__main__":
    unittest.main()
