from fractions import Fraction
import unittest

from sft.physics.criticality_universality_turbulence_terminal_law_v1 import (
    SPEC,
    cascade_exponents,
    cascade_scale_witness,
    critical_scaling_identities,
    generated_universality_classes,
    mean_field_exponents,
    mean_field_scale_witness,
    theorem_certificate,
    universality_equivalence,
)
from sft.physics.structural_constants import candidate_rows


class Tests(unittest.TestCase):
    def test_critical_exponents_and_identities(self):
        values = mean_field_exponents()
        self.assertEqual(values["beta"], Fraction(1, 2))
        self.assertEqual(values["nu"], Fraction(1, 2))
        self.assertEqual(values["gamma"], 1)
        self.assertEqual(values["delta"], 3)
        self.assertEqual(values["alpha"], ())
        self.assertEqual(values["eta"], ())
        identities = critical_scaling_identities()
        self.assertTrue(identities["widom"])
        self.assertTrue(identities["rushbrooke_with_empty_alpha"])
        self.assertTrue(identities["fisher_with_empty_eta"])

    def test_exact_critical_scale_witness(self):
        for base in range(2, 8):
            for depth in range(1, 8):
                row = mean_field_scale_witness(base, depth)
                self.assertTrue(row["order_square_is_excess"])
                self.assertTrue(row["correlation_square_is_excess"])
                self.assertTrue(row["response_is_linear_in_excess"])
                self.assertTrue(row["field_is_order_cube"])

    def test_cascade_scaling(self):
        exponents = cascade_exponents()
        self.assertEqual(exponents["structure_function"], Fraction(2, 3))
        self.assertEqual(exponents["spectrum_magnitude"], Fraction(5, 3))
        self.assertEqual(exponents["spectrum_orientation"], "falling")
        for base in range(2, 8):
            for depth in range(1, 8):
                row = cascade_scale_witness(base, depth)
                self.assertTrue(row["structure_cube_equals_length_square"])
                self.assertTrue(row["spectrum_cube_equals_wavenumber_fifth"])

    def test_universality_class_census(self):
        rows = generated_universality_classes()
        self.assertEqual(len(rows), 2)
        self.assertFalse(universality_equivalence(rows[0]["class_id"], rows[1]["class_id"]))
        self.assertTrue(universality_equivalence(rows[0]["class_id"], rows[0]["class_id"]))

    def test_invalid_boundaries(self):
        with self.assertRaises(ValueError):
            mean_field_scale_witness(0)
        with self.assertRaises(ValueError):
            mean_field_scale_witness(2, 0)
        with self.assertRaises(ValueError):
            cascade_scale_witness(-1)
        with self.assertRaises(ValueError):
            universality_equivalence("unknown", generated_universality_classes()[0]["class_id"])

    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertTrue(all(theorem_certificate().values()))
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
