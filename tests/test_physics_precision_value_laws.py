"""Focused checks for Physics terminal precision successors."""

from fractions import Fraction
import unittest

from sft.physics.precision_value_laws_v1 import (
    PRECISION_VALUE_SPECS,
    terminal_electroweak_cos_squared,
    terminal_electroweak_sin_squared,
    terminal_proton_planck_squared_ratio,
)
from sft.physics.structural_constants import candidate_rows


class PrecisionValueLawTests(unittest.TestCase):
    def test_exact_weak_share(self) -> None:
        self.assertEqual(
            terminal_electroweak_sin_squared(),
            Fraction(1930922298157999, 8642477221479757),
        )
        self.assertEqual(
            terminal_electroweak_sin_squared() + terminal_electroweak_cos_squared(),
            1,
        )

    def test_exact_hierarchy(self) -> None:
        self.assertEqual(
            terminal_proton_planck_squared_ratio(),
            Fraction(
                255923934603817488008405160690199418432572494970880,
                1511539186407,
            ),
        )

    def test_complete_censuses(self) -> None:
        for spec in PRECISION_VALUE_SPECS:
            rows = candidate_rows(spec)
            self.assertEqual(len(rows), 1024)
            self.assertEqual(len({row["candidate_id"] for row in rows}), 1024)


if __name__ == "__main__":
    unittest.main()
