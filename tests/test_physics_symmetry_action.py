from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.symmetry_action_terminal_law_v1 import (
    SPEC,
    all_dyadic_parts_descend,
    all_reduced_fold_parts_preserve_odd_core,
    charge_preserving_bijections,
    descent_telescopes,
    detour_cannot_lower_action,
    path_action,
)


class SymmetryActionTests(unittest.TestCase):
    def test_fold_odd_core_and_dyadic_descent(self) -> None:
        self.assertTrue(all_reduced_fold_parts_preserve_odd_core(128))
        self.assertTrue(all_dyadic_parts_descend(8))

    def test_complete_partition_symmetry_census(self) -> None:
        self.assertEqual(
            len(charge_preserving_bijections(("a", "a", "b", "b"))), 4
        )

    def test_descent_telescopes_exactly(self) -> None:
        path = (
            Fraction(1, 1),
            Fraction(3, 4),
            Fraction(1, 2),
            Fraction(1, 4),
        )
        self.assertTrue(descent_telescopes(path))
        self.assertEqual(path_action(path), Fraction(3, 4))

    def test_detour_retains_extra_positive_action(self) -> None:
        path = (
            Fraction(1, 1),
            Fraction(1, 2),
            Fraction(3, 4),
            Fraction(1, 4),
        )
        self.assertTrue(detour_cannot_lower_action(path))
        self.assertGreater(path_action(path), Fraction(3, 4))

    def test_spec_is_depth_independent_and_parameter_free(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 9)
        self.assertEqual(SPEC.provenance[0].value, "forward_forcing")


if __name__ == "__main__":
    unittest.main()
