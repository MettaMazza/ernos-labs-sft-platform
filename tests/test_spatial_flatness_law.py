from fractions import Fraction
from pathlib import Path
import unittest

from sft.engine import EMPTY_ONE
from sft.physics.spatial_flatness_law import (
    SPATIAL_FLATNESS_SPEC,
    closed_partition,
    refine_partition,
)
from sft.physics.spatial_flatness_validation import (
    SOURCE_PATH,
    planck_interval_contains_absence,
)
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class SpatialFlatnessLawTests(unittest.TestCase):
    def test_complete_partition_returns_structural_absence(self) -> None:
        parts = (Fraction(1, 3), Fraction(2, 3))
        self.assertIs(closed_partition(parts), EMPTY_ONE)

    def test_positive_refinement_preserves_closure(self) -> None:
        parts = (Fraction(1, 3), Fraction(2, 3))
        refined = refine_partition(parts, 1, Fraction(1, 6), Fraction(1, 2))
        self.assertIs(closed_partition(refined), EMPTY_ONE)

    def test_incomplete_partition_halts(self) -> None:
        with self.assertRaises(ValueError):
            closed_partition((Fraction(1, 3), Fraction(1, 3)))

    def test_candidate_product_is_complete(self) -> None:
        self.assertEqual(len(candidate_rows(SPATIAL_FLATNESS_SPEC)), 2048)

    def test_complete_planck_interval_contains_absence(self) -> None:
        self.assertTrue(planck_interval_contains_absence(ROOT / SOURCE_PATH))


if __name__ == "__main__":
    unittest.main()
