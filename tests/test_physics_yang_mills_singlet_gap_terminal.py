from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.yang_mills_singlet_gap_terminal_law_v1 import (
    SPEC,
    physical_singlet_support,
    singlet_gap_trace,
    strong_gap_partition,
)


class YangMillsSingletGapTerminalTests(unittest.TestCase):
    def test_exact_partition_and_orbit(self) -> None:
        partition = strong_gap_partition()
        self.assertEqual(partition["gap"], Fraction(1, 3))
        self.assertEqual(partition["coupling"], Fraction(2, 3))
        self.assertTrue(partition["complete"])
        self.assertTrue(partition["gap_to_coupling"])
        self.assertTrue(partition["coupling_to_gap"])

    def test_physical_singlet_boundary(self) -> None:
        support = physical_singlet_support()
        self.assertEqual(support["least_singlet_constituents"], 2)
        self.assertEqual(support["isolated_colour_observation_record"], ())
        self.assertEqual(support["vacuum_excitation_record"], ())

    def test_massless_carrier_is_not_gapless_singlet(self) -> None:
        trace = singlet_gap_trace(20)
        self.assertTrue(trace["all_gaps_positive"])
        self.assertTrue(trace["gap_depth_invariant"])
        self.assertTrue(trace["work_positive_and_increasing"])
        self.assertTrue(trace["local_carrier_One_speed"])
        self.assertTrue(trace["local_carrier_confined"])
        self.assertTrue(trace["local_masslessness_not_physical_gaplessness"])

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertIn("No continuum", SPEC.grammar_boundary)


if __name__ == "__main__":
    unittest.main()
