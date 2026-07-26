import unittest
from fractions import Fraction

from sft.physics.dark_smithion_lfv_terminal_law_v1 import (
    SPEC,
    abundance_certificate,
    coloured_product,
    lfv_certificate,
    smithion_spectrum_census,
    theorem_certificate,
)
from sft.physics.structural_constants import candidate_rows


class DarkSmithionLfvTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2048)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2048)

    def test_quark_cross_lock_and_smithion_roots(self):
        self.assertEqual(coloured_product(3, 5), Fraction(3, 1454))
        self.assertEqual(coloured_product(3, 7), Fraction(3, 13118))
        spectra = smithion_spectrum_census()
        self.assertEqual(tuple(row["depth"] for row in spectra), (7, 10, 9, 12))
        self.assertEqual(sum(len(row["roots"]) for row in spectra), 12)
        self.assertTrue(theorem_certificate()["all_roots_disjoint_positive"])

    def test_abundance_and_lfv(self):
        self.assertEqual(abundance_certificate()["dark_to_baryon"], Fraction(27, 5))
        self.assertEqual(abundance_certificate()["matter_to_baryon"], Fraction(32, 5))
        lfv = lfv_certificate()
        self.assertEqual(tuple(lfv["weights"].values()), (Fraction(1, 32), Fraction(5, 96), Fraction(5, 24)))
        self.assertEqual(lfv["integer_ratio"], (3, 5, 20))
        self.assertEqual(lfv["tau_ratio"], 4)


if __name__ == "__main__":
    unittest.main()
