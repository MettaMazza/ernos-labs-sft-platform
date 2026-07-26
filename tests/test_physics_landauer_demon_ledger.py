from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.landauer_demon_ledger_terminal_law_v1 import (
    SPEC,
    demon_cycle_ledger,
    erased_distinction_count,
    fold_part,
    minimum_throw,
    reset_preimages,
)


class LandauerDemonLedgerTests(unittest.TestCase):
    def test_reset_fibre(self) -> None:
        self.assertEqual(tuple(fold_part(value) for value in reset_preimages()), (Fraction(1, 2), Fraction(1, 2)))

    def test_exact_cost(self) -> None:
        self.assertEqual(erased_distinction_count(), 1)
        self.assertEqual(minimum_throw(), Fraction(1, 2))

    def test_closed_demon_ledger(self) -> None:
        self.assertTrue(demon_cycle_ledger()["complete"])

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)


if __name__ == "__main__":
    unittest.main()
