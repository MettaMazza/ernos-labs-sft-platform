import unittest
from fractions import Fraction

from sft.physics.higgs_symmetry_terminal_law_v1 import (
    SPEC,
    active_scalar_directions,
    displaced_ground,
    generation_cover_depth,
    leading_higgs_rungs,
    route_cross_lock,
    scalar_direction_support,
    terminal_higgs_mass_ratio,
    terminal_higgs_self_coupling,
    vacuum_ground_census,
)
from sft.physics.structural_constants import candidate_rows


class HiggsSymmetryTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2048)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2048)

    def test_unique_displaced_ground_and_leading_controls(self):
        self.assertEqual(len(vacuum_ground_census()), 3)
        self.assertEqual(displaced_ground(), Fraction(1, 2))
        self.assertEqual(leading_higgs_rungs(), (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)))

    def test_terminal_support_and_values(self):
        self.assertEqual(scalar_direction_support(), 6)
        self.assertEqual(active_scalar_directions(), generation_cover_depth())
        self.assertEqual(active_scalar_directions(), 5)
        self.assertEqual(terminal_higgs_mass_ratio(), Fraction(2563352914777, 5038463954690))
        self.assertEqual(terminal_higgs_self_coupling(), Fraction(6570778165695741824959729, 50772238045420788745992200))
        self.assertTrue(route_cross_lock()["routes_equal"])


if __name__ == "__main__":
    unittest.main()
