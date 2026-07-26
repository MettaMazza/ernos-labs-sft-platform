from __future__ import annotations

import unittest

from sft.physics.fold_universe_transport_terminal_law_v1 import (
    SPEC,
    composite_period,
    crt_component_census,
    denominator_trace,
    target_trajectory_independent_of_source,
)


class FoldUniverseTransportTerminalTests(unittest.TestCase):
    def test_composite_maps(self) -> None:
        for left, right in ((3, 5), (3, 7), (5, 7)):
            with self.subTest(left=left, right=right):
                census = crt_component_census(left, right)
                self.assertTrue(census["bijection"])
                self.assertTrue(census["fold_commutes"])

    def test_periods(self) -> None:
        self.assertTrue(all(composite_period(left, right)["matches"] for left, right in ((3, 5), (3, 7), (5, 7))))

    def test_denominator_and_no_steering(self) -> None:
        self.assertEqual(denominator_trace(1, 15, 8), (15,) * 8)
        self.assertTrue(target_trajectory_independent_of_source(5, 7, 1, 12))

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)


if __name__ == "__main__":
    unittest.main()
