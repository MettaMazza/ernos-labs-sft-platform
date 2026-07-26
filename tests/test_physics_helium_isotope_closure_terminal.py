import unittest
from fractions import Fraction

from sft.physics.helium_isotope_closure_terminal_law_v1 import SPEC, isotope_closure_ledger, theorem_certificate
from sft.physics.structural_constants import candidate_rows


class HeliumIsotopeClosureTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_exact_isotope_partition(self):
        ledger = isotope_closure_ledger()
        self.assertEqual(ledger["complete_cell_count"], 60)
        self.assertEqual(ledger["isotope_conversion"], Fraction(59, 60))
        self.assertEqual(ledger["physical_helium_isotope_share"], Fraction(59, 240))
        self.assertEqual(ledger["physical_hydrogen_family_share"], Fraction(181, 240))
        self.assertTrue(ledger["partition_closes"])

    def test_complete_theorem_certificate(self):
        self.assertTrue(all(theorem_certificate().values()))


if __name__ == "__main__":
    unittest.main()
