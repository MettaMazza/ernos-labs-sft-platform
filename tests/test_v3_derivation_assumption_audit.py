from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
REMEDIATION_IDS = (
    "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
    "SFT-PHYS-SPACE-DIMENSION-THREE-001",
    "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
    "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
    "SFT-PHYS-VALIDATION-INVERSE-SQUARE-001",
)


class DerivationAssumptionAuditTests(unittest.TestCase):
    def test_audit_binds_the_authoritative_407_step_hash(self) -> None:
        audit = json.loads((ROOT / "audits/v3_derivation_assumption_audit_2026-07-24.json").read_text())
        prior = json.loads((ROOT / "prior-work-ledger/manifest.json").read_text())
        prior_hash = next(
            artifact["sha256"]
            for entry in prior["entries"]
            for artifact in entry["artifacts"]
            if artifact["path"] == "OneFoldMaster.md"
        )
        self.assertEqual(audit["authoritative_v2"]["numbered_steps"], 407)
        self.assertEqual(audit["authoritative_v2"]["sha256"], prior_hash)

    def test_every_physical_remediation_has_an_admitted_receipt(self) -> None:
        census = json.loads((ROOT / "census/claims.json").read_text())
        rows = {row["claim_id"]: row for row in census["claims"]}
        for claim_id in REMEDIATION_IDS:
            with self.subTest(claim_id=claim_id):
                self.assertTrue(rows[claim_id]["model_admitted"])
                receipt = json.loads((ROOT / rows[claim_id]["receipt_path"]).read_text())
                self.assertEqual(receipt["receipt_hash"], rows[claim_id]["receipt_hash"])
                self.assertTrue(receipt["accepted_evidence"])
                self.assertTrue(receipt["model_admitted"])
                self.assertEqual(receipt["violations"], [])
                self.assertTrue(all(gate["passed"] for gate in receipt["gate_results"]))

    def test_measurement_checker_is_downstream_only(self) -> None:
        note = (ROOT / "claims/SFT-PHYS-MEAS-BOUNDARY-GROWTH-001/WHY_DERIVATION_CHECK.md").read_text()
        correction = (ROOT / "claims/SFT-PHYS-MEAS-BOUNDARY-GROWTH-001/CORRECTION_2026-07-24.md").read_text()
        inverse_registration = json.loads(
            (ROOT / "claims/SFT-PHYS-FIELD-INVERSE-SQUARE-001/registration.json").read_text()
        )
        self.assertIn("independent exact\nchecker", note)
        self.assertIn("already be forced and sealed", note)
        self.assertIn("never become the source", note)
        self.assertIn("no measured exponent", correction)
        self.assertNotIn("SFT-PHYS-MEAS-BOUNDARY-GROWTH-001", inverse_registration["dependencies"])

    def test_native_computation_results_are_replication_gaps_not_open_sft_questions(self) -> None:
        frontier = (ROOT / "frontier/computation.md").read_text()
        self.assertIn("V2-closed theorems", frontier)
        self.assertIn("V3 model admissions", frontier)
        for step in ("Step 404", "Step 405", "Step 406"):
            self.assertIn(step, frontier)

    def test_unbounded_finite_fault_law_is_not_called_a_hardware_threshold(self) -> None:
        frontier = (ROOT / "frontier/quantum_computation.md").read_text()
        clarification = (
            ROOT / "claims/SFT-QUANTUM-FAULT-TOLERANCE-001/AUDIT_CLARIFICATION_2026-07-24.md"
        ).read_text()
        self.assertIn("positive-finite fault family is not a frontier", frontier)
        self.assertIn("mathematical law is already unbounded", clarification)
        self.assertIn("hardware noise thresholds", clarification)


if __name__ == "__main__":
    unittest.main()
