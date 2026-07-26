from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.lattice_operator_terminal_law_v1 import (
    SPEC,
    causal_ball_count,
    conservative_stencil,
    cyclic_update,
    exact_mode_carriers,
    point_source_operator,
)


class LatticeOperatorTerminalTests(unittest.TestCase):
    def test_stencils(self) -> None:
        self.assertEqual(conservative_stencil(1)["neighbour_share"], Fraction(1, 4))
        self.assertEqual(conservative_stencil(2)["neighbour_share"], Fraction(1, 8))
        self.assertEqual(conservative_stencil(3)["complete_total"], Fraction(1, 1))

    def test_bump_and_flat_state(self) -> None:
        bump = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
        self.assertEqual(cyclic_update(bump)[1], Fraction(3, 8))
        flat = (Fraction(1, 5),) * 5
        self.assertEqual(cyclic_update(flat), flat)

    def test_point_sources(self) -> None:
        self.assertEqual(point_source_operator(2)["peak_magnitude"], 4)
        self.assertEqual(point_source_operator(3)["ring_count"], 6)
        self.assertTrue(point_source_operator(3)["balanced_magnitude"])

    def test_causal_counts(self) -> None:
        self.assertEqual(tuple(causal_ball_count(2, tick) for tick in (1, 2, 3)), (5, 13, 25))
        self.assertEqual(tuple(causal_ball_count(3, tick) for tick in (1, 2, 3)), (7, 25, 63))

    def test_modes_and_spec(self) -> None:
        modes = exact_mode_carriers(7)
        self.assertEqual(len(modes), 7)
        self.assertEqual(sum(mode.identity_phase for mode in modes), 1)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
