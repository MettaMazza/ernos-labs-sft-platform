from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.coupling_accumulated_separation_terminal_law_v1 import (
    SPEC,
    accumulation_is_bounded,
    adjacent_sector_gap,
    finite_partial_accumulation,
    finite_tail_envelope,
    successor_is_below_half,
    tolerance_is_witnessed,
)


class CouplingAccumulatedSeparationTests(unittest.TestCase):
    def test_first_terms_and_forced_envelope(self) -> None:
        self.assertEqual(adjacent_sector_gap(1), Fraction(1, 12))
        self.assertEqual(adjacent_sector_gap(2), Fraction(1, 20))
        self.assertEqual(
            Fraction(1, 12) + 2 * Fraction(1, 20), Fraction(11, 60)
        )

    def test_every_checked_partial_sum_obeys_depth_independent_law(self) -> None:
        for level in range(1, 129):
            self.assertTrue(accumulation_is_bounded(level))
            self.assertLess(finite_partial_accumulation(level), Fraction(11, 60))

    def test_contraction_and_tail_envelope(self) -> None:
        for level in range(2, 129):
            self.assertTrue(successor_is_below_half(level))
            self.assertTrue(finite_tail_envelope(2, level))

    def test_every_checked_positive_tolerance_has_finite_witness(self) -> None:
        for denominator in (1, 2, 3, 5, 7, 11, 127, 1024, 65537):
            self.assertTrue(tolerance_is_witnessed(denominator))

    def test_spec_is_exact_and_parameter_free(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 8)
        self.assertEqual(SPEC.provenance[0].value, "forward_forcing")


if __name__ == "__main__":
    unittest.main()
