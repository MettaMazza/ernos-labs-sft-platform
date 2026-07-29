from fractions import Fraction
import unittest

from sft.physics.unified_constants_object_law_v1 import (
    SECTOR_NODES,
    SPEC,
    admitted_terminal_vector,
    dependency_graph,
    foundation_order_vector,
    reachable_from_one,
    theorem_certificate,
)


class UnifiedConstantsObjectTests(unittest.TestCase):
    def test_foundation_order_exact(self):
        vector = foundation_order_vector(3)
        self.assertEqual(vector["inverse_fine_structure_leading"], Fraction(34259, 250))
        self.assertEqual(vector["charged_lepton_leading_product"], Fraction(1, 485))
        self.assertEqual(vector["down_cover_conjugate"], Fraction(1, 95))
        self.assertEqual(vector["up_cover_product"], Fraction(1, 383))
        self.assertEqual(vector["dark_to_baryon_leading"], Fraction(27, 5))
        self.assertEqual(vector["dark_share_leading"], Fraction(27, 32))
        self.assertEqual(vector["hubble_leading"], Fraction(13, 12))
        self.assertEqual(vector["planck_hierarchy_exponent"], Fraction(127, 2))
        self.assertEqual(vector["local_vacuum_energy_floor"], Fraction(1, 2**20))
        self.assertEqual(vector["half_One"], Fraction(1, 2))

    def test_terminal_cross_sector_readings(self):
        vector = admitted_terminal_vector()
        self.assertEqual(vector["inverse_fine_structure_terminal"], Fraction(503846395469, 3676744786))
        self.assertEqual(vector["charged_lepton_sharpened_product"], Fraction(3, 1454))
        self.assertEqual(vector["down_quark_terminal_product"], Fraction(1, 383))
        self.assertEqual(vector["up_quark_terminal_product"], Fraction(1, 3071))
        self.assertEqual(vector["dark_to_baryon_terminal"], Fraction(279, 52))
        self.assertEqual(vector["hubble_terminal"], Fraction(3305, 3048))
        self.assertEqual(vector["planck_hierarchy_exponent"], Fraction(127, 2))
        self.assertEqual(vector["local_vacuum_amplitude_floor"], Fraction(1, 2**10))
        self.assertEqual(vector["local_vacuum_energy_floor"], Fraction(1, 2**20))
        self.assertEqual(vector["normalized_cosmological_magnitude"], Fraction(33, 16))

    def test_rooted_dependency_object(self):
        self.assertTrue(SECTOR_NODES.issubset(reachable_from_one(dependency_graph())))

    def test_dependency_and_independence_probe(self):
        certificate = theorem_certificate()
        self.assertTrue(certificate["every_generator_dependent_carrier_moves"])
        self.assertTrue(certificate["independent_controls_hold"])
        self.assertTrue(certificate["leading_terminal_cross_lock"])

    def test_complete_candidate_grammar(self):
        cardinality = 1
        for axis in SPEC.axes:
            cardinality *= len(axis.choices)
        self.assertEqual(cardinality, 4096)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
