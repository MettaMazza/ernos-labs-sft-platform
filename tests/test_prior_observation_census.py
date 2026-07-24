from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "audits/v2_407_step_observation_census.json"


class PriorObservationCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.census = json.loads(CENSUS.read_text(encoding="utf-8"))

    def test_every_v2_step_is_registered_once_and_in_order(self) -> None:
        rows = self.census["steps"]
        self.assertEqual([row["step"] for row in rows], list(range(1, 408)))
        self.assertTrue(all(row["source_block_sha256"].startswith("sha256:") for row in rows))

    def test_prior_results_are_observations_not_derivation_inputs(self) -> None:
        policy = self.census["policy"]
        self.assertTrue(policy["prior_results_are_observational_data"])
        self.assertTrue(policy["prior_results_define_reconstruction_obligations"])
        self.assertFalse(policy["prior_answer_artifacts_may_enter_v3_derivation"])
        self.assertFalse(policy["prior_observation_may_select_v3_candidate_or_survivor"])

    def test_unmapped_steps_block_completion(self) -> None:
        self.assertEqual(self.census["mapped_step_count"], 118)
        self.assertEqual(self.census["unmapped_step_count"], 289)
        self.assertEqual(self.census["same_strength_closed_step_count"], 4)
        self.assertEqual(self.census["same_strength_open_step_count"], 403)
        self.assertGreater(self.census["unmapped_step_count"], 0)
        self.assertTrue(self.census["status"].startswith("open_blocking"))

    def test_inverse_alpha_is_mapped_to_physics_before_chemistry(self) -> None:
        row = next(row for row in self.census["steps"] if row["step"] == 5)
        self.assertIn("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", row["explicit_v3_claim_ids"])
        self.assertIn("SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001", row["explicit_v3_claim_ids"])
        self.assertEqual(row["explicit_mapping_status"], "mapped_to_current_admitted_claims")

    def test_failed_empirical_attempt_is_preserved_beneath_resolved_refinement(self) -> None:
        row = next(row for row in self.census["steps"] if row["step"] == 6)
        self.assertEqual(row["explicit_mapping_status"], "mapped_to_current_admitted_claims")
        disposition = row["same_strength_disposition"]
        self.assertTrue(disposition["closed"])
        self.assertEqual(
            disposition["status"],
            "closed_by_formal_reconstruction_and_empirically_admitted_terminal_refinement",
        )
        self.assertEqual(
            disposition["failed_receipt_hash"],
            "sha256:2b7023f72254b172e690e820cd99fa75810c261b6956bfc40dbb22ce63c66439",
        )
        self.assertEqual(
            disposition["admitted_receipt_hash"],
            "sha256:c74f9c45eab7c232ebf85fe2fd5aea24f07d167df3857dad50ffcc5c34732294",
        )

    def test_koide_step_is_closed_by_exact_all_interval_validation(self) -> None:
        row = next(row for row in self.census["steps"] if row["step"] == 14)
        self.assertEqual(row["explicit_mapping_status"], "mapped_to_current_admitted_claims")
        self.assertTrue(row["same_strength_disposition"]["closed"])
        self.assertEqual(
            row["same_strength_disposition"]["admitted_receipt_hash"],
            "sha256:369a1e48d622bba0f3e4abc1e89fef8553b17097c3d8c4427afca26386f6cbf9",
        )

    def test_dark_baryon_step_is_jointly_closed(self) -> None:
        row = next(row for row in self.census["steps"] if row["step"] == 7)
        self.assertTrue(row["same_strength_disposition"]["closed"])
        self.assertEqual(
            row["same_strength_disposition"]["admitted_receipt_hash"],
            "sha256:38b06863d5a59f8f8ea17fee7a0a1d5ff1fdcd0c6f7b9de3e9f635705d4f8cc2",
        )

    def test_hubble_step_is_reconstructed_and_jointly_closed(self) -> None:
        row = next(row for row in self.census["steps"] if row["step"] == 8)
        self.assertEqual(row["explicit_v3_claim_ids"], ["SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001"])
        self.assertTrue(row["same_strength_disposition"]["closed"])
        self.assertEqual(
            row["same_strength_disposition"]["admitted_receipt_hash"],
            "sha256:d4ce8d8568e94b5032fc65633d024aaa7cba6365e6d88217c61ec9a388153e88",
        )


if __name__ == "__main__":
    unittest.main()
