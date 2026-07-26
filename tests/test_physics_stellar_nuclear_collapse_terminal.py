import unittest

from sft.physics.stellar_nuclear_collapse_terminal_law_v1 import (
    EMPTY_ONE_FORM,
    SPEC,
    binding_terminal,
    charged_boundary_paths,
    neutral_capture_trace,
    stellar_chain_certificate,
    support_loss_collapse,
    theorem_certificate,
    thermonuclear_certificate,
)
from sft.physics.structural_constants import candidate_rows


class StellarNuclearCollapseTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)

    def test_depth_independent_stage_order_and_nesting(self):
        for count in (1, 2, 3, 6, 16, 32):
            certificate = stellar_chain_certificate(count)
            self.assertTrue(certificate["all_access_carriers_strict"])
            self.assertTrue(certificate["strictly_nested"])
            self.assertTrue(certificate["depth_independent_successor"])
        self.assertLess(charged_boundary_paths(32), charged_boundary_paths(33))

    def test_binding_terminal_and_support_loss(self):
        terminal = binding_terminal()
        self.assertEqual((terminal["mass_count"], terminal["charge_count"], terminal["neutron_count"]), (62, 28, 34))
        self.assertTrue(terminal["unique"])
        self.assertTrue(terminal["tail_closed"])
        self.assertEqual(terminal["ordinary_fusion_release_beyond_terminal"], EMPTY_ONE_FORM)
        collapse = support_loss_collapse()
        self.assertTrue(collapse["outward_fusion_support_empty"])
        self.assertTrue(collapse["inward_gravity_retained"])
        self.assertEqual(len(collapse["finite_endpoint_classes"]), 2)

    def test_two_explosion_and_heavy_element_channels(self):
        for count in (1, 2, 3, 5, 8):
            runaway = thermonuclear_certificate(count)
            self.assertTrue(runaway["no_interior_fixed_point"])
            self.assertTrue(runaway["finite_terminal"])
            capture = neutral_capture_trace(count)
            self.assertTrue(capture["charged_Coulomb_boundary_absent"])
            self.assertTrue(capture["capture_precedes_label_rebalance"])
            self.assertTrue(capture["mass_support_retained"])
        theorem = theorem_certificate()
        self.assertTrue(theorem["all_thermonuclear_finite"])
        self.assertTrue(theorem["all_neutral_capture_closed"])


if __name__ == "__main__":
    unittest.main()
