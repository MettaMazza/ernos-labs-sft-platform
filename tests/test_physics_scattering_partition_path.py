from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.scattering_partition_path_terminal_law_v1 import (
    SPEC,
    cross_section,
    larger_section_shortens_path,
    mean_free_path,
    partition_is_complete,
    two_fibre_outcome_measure,
)


class ScatteringPartitionPathTests(unittest.TestCase):
    def test_complete_two_fibre_partition(self) -> None:
        self.assertEqual(two_fibre_outcome_measure(("scatter", "pass")), (Fraction(1, 2), Fraction(1, 2)))
        self.assertTrue(partition_is_complete(("scatter", "pass")))

    def test_cross_section_is_counted_support(self) -> None:
        self.assertEqual(cross_section(1, 2), Fraction(1, 2))

    def test_v2_path_witnesses(self) -> None:
        self.assertEqual(mean_free_path(Fraction(1, 1), Fraction(1, 1)), Fraction(1, 1))
        self.assertEqual(mean_free_path(Fraction(1, 1), Fraction(1, 2)), Fraction(2, 1))

    def test_larger_section_shortens_path(self) -> None:
        self.assertTrue(larger_section_shortens_path(Fraction(3, 2), Fraction(1, 4), Fraction(1, 2)))

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 9)


if __name__ == "__main__":
    unittest.main()
