import unittest
from fractions import Fraction

from sft.physics.strong_cp_baryon_stability_terminal_law_v1 import (
    EMPTY_ONE,
    ONE,
    SPEC,
    proton_transition_certificate,
    sector_action_certificate,
    strong_alignment_certificate,
    strong_hand_census,
)
from sft.physics.structural_constants import candidate_rows


class StrongCpBaryonStabilityTerminalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 2048)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2048)

    def test_strong_phase_is_uniquely_aligned(self):
        rows = strong_hand_census()
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["complete_colour_hand_product"] for row in rows), 1)
        certificate = strong_alignment_certificate()
        self.assertEqual(certificate["strong_phase"], ("aligned-One", ONE))
        self.assertEqual(certificate["weak_phase"], ("self-antipodal-half-One", Fraction(1, 2)))
        self.assertEqual(certificate["electric_dipole_carrier"], EMPTY_ONE)
        self.assertEqual(certificate["extra_compensator_required"], EMPTY_ONE)

    def test_all_sector_actions_preserve_fibre(self):
        certificate = sector_action_certificate()
        self.assertEqual(certificate["mediator_counts"], (3, 8, 24, 48))
        self.assertEqual(certificate["mediator_total"], 83)
        self.assertTrue(certificate["all_actions_fibre_preserving"])
        self.assertEqual(certificate["cross_fibre_pair_count"], 202)
        self.assertEqual(certificate["quark_to_lepton_pair_count"], 6)
        self.assertEqual(certificate["generated_cross_fibre_actions"], ())

    def test_proton_baryon_One_is_invariant(self):
        certificate = proton_transition_certificate()
        self.assertEqual(certificate["initial_baryon_tally"], ONE)
        self.assertEqual(certificate["generated_image_count"], 27)
        self.assertTrue(certificate["all_images_retain_baryon_One"])
        self.assertEqual(certificate["lepton_only_decay_image"], EMPTY_ONE)


if __name__ == "__main__":
    unittest.main()
