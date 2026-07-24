from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class PhysicsPriorValueAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(
            (ROOT / "audits/physics_prior_value_audit_2026-07-24.json").read_text()
        )

    def test_published_and_live_physics_surfaces_are_not_conflated(self) -> None:
        self.assertEqual(self.audit["published_physics_claim_count"], 140)
        self.assertEqual(self.audit["current_physics_claim_count"], 159)
        self.assertEqual(len(self.audit["postpublication_physics_claim_ids"]), 19)

    def test_inverse_alpha_is_owned_by_physics_and_missing_from_v1_paper(self) -> None:
        alpha = self.audit["inverse_alpha"]
        self.assertEqual(alpha["owning_branch"], "physics")
        self.assertFalse(alpha["published_physics_v1_contains_claim"])
        self.assertTrue(alpha["categorical_publication_failure"])

    def test_relation_checks_are_not_called_forced_absolute_values(self) -> None:
        values = self.audit["published_numeric_correspondence_classification"]
        self.assertEqual(values["reported_count"], 14)
        self.assertEqual(values["measured_input_relation_checks"], 13)
        self.assertEqual(values["measured_interval_cross_analysis_checks"], 1)
        self.assertEqual(values["root_forced_absolute_external_values"], 0)

    def test_audit_blocks_materials_resumption(self) -> None:
        self.assertEqual(self.audit["status"], "open_blocking")
        self.assertTrue(self.audit["materials_work_paused"])

    def test_charged_lepton_failed_attempt_is_resolved_without_erasure(self) -> None:
        row = self.audit["charged_lepton_cubic"]
        self.assertEqual(row["formal_status"], "independently_replicated")
        self.assertEqual(row["candidate_count"], 2304)
        self.assertEqual(row["empirical_validation_status"], "resolved_by_terminal_refinement")
        self.assertTrue(row["same_strength_prior_disposition_closed"])
        self.assertEqual(row["terminal_provenance"], "observational_derivation")
        self.assertEqual(
            row["terminal_admission_receipt_hash"],
            "sha256:c74f9c45eab7c232ebf85fe2fd5aea24f07d167df3857dad50ffcc5c34732294",
        )
        self.assertEqual(
            row["koide_validation_receipt_hash"],
            "sha256:369a1e48d622bba0f3e4abc1e89fef8553b17097c3d8c4427afca26386f6cbf9",
        )

    def test_charged_lepton_failure_is_preserved_outside_the_model(self) -> None:
        failure = json.loads(
            (ROOT / "audits/physics_charged_lepton_empirical_failure.json").read_text()
        )
        self.assertEqual(failure["halted_stage"], "empirical_validation")
        self.assertFalse(failure["comparison"]["all_rows_passed"])
        self.assertFalse(failure["comparison"]["muon_electron"]["overlap"])
        self.assertFalse(failure["comparison"]["muon_tau"]["overlap"])
        census = json.loads((ROOT / "census/claims.json").read_text())
        self.assertNotIn(
            "SFT-PHYS-VALIDATION-CHARGED-LEPTON-CUBIC-001",
            {claim["claim_id"] for claim in census["claims"]},
        )

    def test_dark_baryon_value_is_jointly_closed(self) -> None:
        row = self.audit["dark_baryon_fraction"]
        self.assertEqual(row["leading_ratio"], "27/5")
        self.assertEqual(row["refined_ratio"], "279/52")
        self.assertTrue(row["same_strength_prior_disposition_closed"])
        self.assertEqual(
            row["admission_receipt_hash"],
            "sha256:38b06863d5a59f8f8ea17fee7a0a1d5ff1fdcd0c6f7b9de3e9f635705d4f8cc2",
        )

    def test_hubble_calibration_is_jointly_closed_at_exact_ratio_boundary(self) -> None:
        row = self.audit["hubble_calibration"]
        self.assertEqual(row["leading_ratio"], "13/12")
        self.assertEqual(row["refined_ratio"], "3305/3048")
        self.assertEqual(row["external_ratio_interval"], ["720/679", "3704/3345"])
        self.assertTrue(row["same_strength_prior_disposition_closed"])
        self.assertEqual(row["provenance"], "observational_derivation")
        self.assertEqual(
            row["admission_receipt_hash"],
            "sha256:d4ce8d8568e94b5032fc65633d024aaa7cba6365e6d88217c61ec9a388153e88",
        )

    def test_spatial_flatness_uses_absence_and_complete_curvature_record(self) -> None:
        row = self.audit["spatial_flatness"]
        self.assertIn("empty One curvature remainder", row["exact_result"])
        self.assertEqual(row["external_record"]["central_magnitude"], "7/10000")
        self.assertEqual(row["external_record"]["uncertainty_magnitude"], "19/10000")
        self.assertTrue(row["same_strength_prior_disposition_closed"])
        self.assertEqual(
            row["admission_receipt_hash"],
            "sha256:ec8cf537a7460687e1ca3d1c9e5d1781b96b477e4c11f68d7c3208e82d3d1a66",
        )

    def test_physics_successor_publication_gate_fails_closed(self) -> None:
        from tools.verify_physics_successor_gate import blockers

        failures = blockers()
        self.assertTrue(failures)
        self.assertTrue(any("V1 observations" in failure for failure in failures))
        self.assertTrue(any("V2 steps" in failure for failure in failures))
        self.assertTrue(any("inverse alpha" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
