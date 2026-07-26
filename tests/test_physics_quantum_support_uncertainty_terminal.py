from fractions import Fraction
import unittest

from sft.physics.quantum_support_uncertainty_terminal_law_v1 import (
    SPEC,
    bell_local_record_census,
    binary_words,
    complete_walsh_census,
    coprime_trace_census,
    joint_subset_census,
    measurement_partition,
    preparation_depth,
    setting_inclusive_no_signal_support,
    spacing_cancellation_certificate,
    theorem_certificate,
    walsh_support_certificate,
)
from sft.physics.structural_constants import candidate_rows


class QuantumSupportUncertaintyTerminalTests(unittest.TestCase):
    def test_complete_walsh_support_census(self):
        census = complete_walsh_census(4)
        self.assertEqual(census["candidate_supports"], 65808)
        self.assertGreater(census["saturated_supports"], 1)
        self.assertTrue(census["all_pass"])

    def test_exact_support_and_spread_bounds(self):
        for depth in range(1, 5):
            words = binary_words(depth)
            for selected in ((words[0],), words):
                row = walsh_support_certificate(depth, selected)
                self.assertTrue(row["parseval_identity"])
                self.assertTrue(row["support_bound"])
                self.assertTrue(row["unit_free_bound"])
                self.assertTrue(row["squared_grid_bound"])
        depth_two = walsh_support_certificate(2, binary_words(2)[:2])
        self.assertEqual(depth_two["squared_grid_spread_product"], Fraction(1, 16))
        self.assertEqual(depth_two["squared_grid_floor"], Fraction(1, 16))

    def test_spacing_cancels(self):
        selected = (binary_words(3)[0],)
        for spacing in (Fraction(1, 8), Fraction(2, 9), Fraction(3, 7), Fraction(5, 11)):
            row = spacing_cancellation_certificate(3, selected, spacing)
            self.assertTrue(row["spacing_cancelled"])
            self.assertEqual(row["product"], 1)

    def test_preparation_fixes_measurement_depth(self):
        self.assertEqual(preparation_depth(8)["depth"], 3)
        self.assertEqual(preparation_depth(8)["branch_unit"], Fraction(1, 8))
        partition = measurement_partition(3, (1,) * 8)
        self.assertTrue(partition["maximal_resolution"])
        self.assertTrue(partition["weights_sum_to_one"])
        with self.assertRaises(ValueError):
            preparation_depth(6)

    def test_complete_joint_factorability_censuses(self):
        two_three = joint_subset_census(2, 3)
        self.assertEqual((two_three["nonempty_supports"], two_three["factorable_supports"], two_three["nonfactorable_supports"]), (63, 21, 42))
        three_five = joint_subset_census(3, 5)
        self.assertEqual((three_five["nonempty_supports"], three_five["factorable_supports"], three_five["nonfactorable_supports"]), (32767, 217, 32550))
        for row in (two_three, three_five):
            self.assertTrue(row["full_product_factorable"])
            self.assertTrue(row["projections_complete"])
            self.assertTrue(row["remote_relabel_invariant"])

    def test_coprime_product_is_not_automatically_entanglement(self):
        for left, right in ((2, 3), (3, 5)):
            row = coprime_trace_census(left, right)
            self.assertTrue(row["one_visit_per_cell"])
            self.assertTrue(row["product_exceeds_sum"])
            self.assertFalse(row["product_alone_is_entanglement"])

    def test_bell_factorization_boundary(self):
        local = bell_local_record_census()
        self.assertEqual(local["strategy_count"], 16)
        self.assertEqual(local["maximum_wins"], 3)
        self.assertEqual(local["local_bound"], Fraction(3, 4))
        inclusive = setting_inclusive_no_signal_support()
        self.assertTrue(inclusive["all_setting_relations_satisfied"])
        self.assertTrue(inclusive["no_signalling"])

    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        self.assertTrue(all(theorem_certificate().values()))
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
