import unittest
from fractions import Fraction

from sft.physics.hadron_regge_dimensional_terminal_law_v1 import SPEC, squared_resonance_carrier, theorem_certificate
from sft.physics.structural_constants import candidate_rows


class HadronReggeDimensionalTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 512)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 512)

    def test_exact_first_five(self):
        self.assertEqual(tuple(squared_resonance_carrier(rank) for rank in range(1, 6)), (Fraction(3, 5), Fraction(9, 5), Fraction(3), Fraction(21, 5), Fraction(27, 5)))

    def test_depth_independent_certificate(self):
        certificate = theorem_certificate()
        self.assertTrue(certificate["all_positive"])
        self.assertTrue(certificate["constant_successor"])
        self.assertTrue(certificate["closed_form"])


if __name__ == "__main__":
    unittest.main()
