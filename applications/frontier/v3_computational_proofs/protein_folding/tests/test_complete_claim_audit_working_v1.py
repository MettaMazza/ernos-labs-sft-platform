from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest


WORKSPACE = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[5]
PAPER_DIR = WORKSPACE / "paper"
AUDIT = PAPER_DIR / "COMPLETE_CLAIM_AUDIT.md"
MANIFEST = PAPER_DIR / "COMPLETE_CLAIM_AUDIT_MANIFEST.json"
RECONCILIATION = PAPER_DIR / "PRELIMINARY_V0_9_4_IDENTITY_RECONCILIATION.json"
MATRIX = REPOSITORY / "publications/preliminary_toe/EXHAUSTIVE_TOE_CONTENT_MATRIX.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompleteClaimAuditWorkingV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = AUDIT.read_text()
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.reconciliation = json.loads(RECONCILIATION.read_text())
        matrix = json.loads(MATRIX.read_text())
        cls.matrix_by_id = {row["claim_id"]: row for row in matrix["claims"]}

    def test_inventory_is_exactly_twenty_one_unique_records(self) -> None:
        ids = self.manifest["claim_ids"]
        self.assertEqual(len(ids), 21)
        self.assertEqual(len(set(ids)), 21)
        self.assertEqual(self.manifest["claim_record_count"], 21)
        self.assertEqual(self.manifest["model_admitted_dependency_count"], 20)
        self.assertEqual(self.manifest["frontier_application_registration_count"], 1)
        for claim_id in ids:
            self.assertEqual(self.audit.count(f"**Claim ID:** `{claim_id}`"), 1)

    def test_every_claim_section_exposes_guidance_fields(self) -> None:
        sections = re.split(r"(?m)^## \d+\. ", self.audit)[1:]
        self.assertEqual(len(sections), 21)
        required = (
            "**Claim ID:**",
            "**Family:**",
            "**Formal status:**",
            "**Empirical status:**",
            "**Closure status:**",
            "### Exact statement",
            "### Reason required and scientific meaning",
            "### Dependency route",
            "### Carrier, boundary, relation and retained record",
            "**Carrier:**",
            "**Relation:**",
            "**Retained record:**",
            "**Evidence class:**",
            "**Provenance:**",
            "**Generality:**",
            "**Extension rule",
            "### Candidate census and uniqueness",
            "### Falsification and controls",
            "### Evidence sources",
            "**Source-capture status:**",
            "**Evidence chronology:**",
            "### Receipt and package identities",
        )
        for section in sections:
            for field in required:
                self.assertIn(field, section, msg=f"missing {field} in {section[:100]}")

    def test_model_claim_values_match_authoritative_matrix(self) -> None:
        for claim_id in self.manifest["claim_ids"][1:]:
            claim = self.matrix_by_id[claim_id]
            marker = f"**Claim ID:** `{claim_id}`"
            start = self.audit.index(marker)
            next_start = self.audit.find("\n## ", start)
            section = self.audit[start : next_start if next_start >= 0 else None]
            self.assertIn(f"**{claim['candidate_count']:,} candidates**", section)
            self.assertIn(f"**{claim['unique_survivor_count']:,} unique survivor**", section)
            self.assertIn(claim["statement"], section)
            self.assertIn(claim["registered_receipt_id"], section)
            for path, sha in claim["package_files"].items():
                self.assertEqual(digest(REPOSITORY / path), sha)
                self.assertIn(path, section)
                self.assertIn(sha, section)

    def test_manifest_binds_every_input_and_output(self) -> None:
        for path, sha in self.manifest["inputs"].items():
            self.assertEqual(digest(REPOSITORY / path), sha)
        for path, sha in self.manifest["outputs"].items():
            self.assertEqual(digest(REPOSITORY / path), sha)
        self.assertFalse(self.manifest["immutable_release_edited"])
        self.assertFalse(self.manifest["protected_authority_edited"])
        self.assertTrue(self.manifest["remote_publication_authorized"])

    def test_identity_discrepancy_is_explicit_and_current_identity_matches(self) -> None:
        frozen = self.reconciliation["frozen_internal_references"]
        self.assertNotEqual(
            frozen["conceptual_paper_workspace_manifest_sha256"],
            frozen["scientific_audit_workspace_manifest_sha256"],
        )
        current = digest(WORKSPACE / "workspace_manifest.json")
        self.assertEqual(self.reconciliation["current_workspace_manifest_sha256"], current)
        self.assertEqual(self.reconciliation["release_machine_manifest_reference"], current)
        self.assertFalse(self.reconciliation["immutable_release_edited"])
        self.assertFalse(self.reconciliation["protected_authority_edited"])
        self.assertTrue(self.reconciliation["remote_publication_authorized"])
        self.assertEqual(self.reconciliation["publication_version"], "0.9.4")
        self.assertEqual(self.reconciliation["version_doi"], "10.5281/zenodo.21717581")


if __name__ == "__main__":
    unittest.main()
