from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.composite_confining_sector_terminal_law_v1 import (
    REGISTERED_COMPOSITE_SECTORS,
    SPEC,
    fold_mode_label,
    holding_coupling,
    inverse_fold_mode_label,
    orbit_partition,
    sector_certificate,
)
from sft.physics.structural_constants import candidate_rows


class CompositeConfiningSectorTerminalTests(unittest.TestCase):
    def test_complete_orbit_partitions(self) -> None:
        self.assertEqual(orbit_partition(8), ((1, 2, 4), (3, 6, 5)))
        self.assertEqual(tuple(len(row) for row in orbit_partition(12)), (10,))
        self.assertEqual(tuple(len(row) for row in orbit_partition(18)), (8, 8))
        self.assertEqual(tuple(len(row) for row in orbit_partition(24)), (11, 11))
        self.assertEqual(tuple(len(row) for row in orbit_partition(30)), (28,))

    def test_bijection_and_confinement(self) -> None:
        for sector in REGISTERED_COMPOSITE_SECTORS:
            certificate = sector_certificate(sector)
            self.assertTrue(certificate["Fold_is_bijective"])
            self.assertTrue(certificate["denominator_preserved"])
            for label in certificate["modes"]:
                self.assertEqual(inverse_fold_mode_label(fold_mode_label(label, sector), sector), label)

    def test_antipodal_pair_counts_and_correction(self) -> None:
        self.assertEqual(tuple(sector_certificate(sector)["antipodal_pair_count"] for sector in REGISTERED_COMPOSITE_SECTORS), (3, 5, 8, 11, 14))
        self.assertTrue(all(sector_certificate(sector)["pairs_are_complete"] and sector_certificate(sector)["pairs_reassemble_One"] for sector in REGISTERED_COMPOSITE_SECTORS))

    def test_exact_couplings(self) -> None:
        self.assertEqual(tuple(holding_coupling(sector) for sector in REGISTERED_COMPOSITE_SECTORS), (Fraction(7, 8), Fraction(11, 12), Fraction(17, 18), Fraction(23, 24), Fraction(29, 30)))

    def test_complete_candidate_product_and_scope(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2048)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2048)
        SPEC.validate()
        self.assertTrue(any("observed independent physical force" in item for item in SPEC.exclusions))
        self.assertTrue(any("measured confirmations" in item for item in SPEC.exclusions))


if __name__ == "__main__":
    unittest.main()
