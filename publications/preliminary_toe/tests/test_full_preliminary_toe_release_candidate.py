from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "publications/preliminary_toe"
MASTER = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
CLAIM_MD = HERE / "appendices/COMPLETE_CLAIM_INVENTORY.md"
CLAIM_JSON = HERE / "appendices/COMPLETE_CLAIM_INVENTORY.json"
FREEZE = HERE / "publication/CORPUS_FREEZE.json"
INVENTORY = HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


class FullPreliminaryToeReleaseCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.master = MASTER.read_text(encoding="utf-8")
        cls.claim_markdown = CLAIM_MD.read_text(encoding="utf-8")
        cls.claim_json = json.loads(CLAIM_JSON.read_text(encoding="utf-8"))
        cls.freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_rejected_overview_is_absent(self) -> None:
        self.assertNotIn("Executive overview", self.master)
        self.assertNotIn("PRELIMINARY COMPLETE SYNTHESIS", self.master)
        self.assertNotIn("19-page", self.master)

    def test_full_scale_and_dependency_topology(self) -> None:
        self.assertGreaterEqual(words(self.master), 100_000)
        required = [
            "## Abstract",
            "## Headline findings",
            "## Current-status statement",
            "## 1. Scope, ownership and publication authority",
            "## 2. The scientific constitution",
            "## 3. Mathematical constitution",
            "## 4. Empirical constitution and chronology",
            "## 5. Dependency spine",
            "Foundation",
            "Mathematics",
            "Information Science",
            "Classical Computation",
            "Reversible and Quantum Computation",
            "Physics",
            "Chemistry",
            "Materials Science",
            "Biology and Life Sciences",
            "Medicine and Health Sciences",
            "Consciousness and Cognitive Science",
            "Earth and Environmental Sciences",
            "Astronomy and Cosmology",
            "Social and Collective Systems",
            "Engineering Translation",
            "Cross-Branch Synthesis",
            "Protein Fold",
            "Chess Fold",
            "Go Fold",
            "Unison Fold AI",
            "## 25. Corpus-wide evidence reconciliation",
            "## 26. Corrections, adverse results and historical custody",
            "## 27. Limitations and open frontier",
            "## 28. Reproducibility",
            "## 29. Data and code availability",
            "## 30. Conclusion",
            "## References and authoritative records",
        ]
        for item in required:
            self.assertIn(item, self.master, item)

    def test_current_counts_and_nonuniform_completion_are_explicit(self) -> None:
        for value in ("2,751", "892,246", "11,004", "42,173,082"):
            self.assertIn(value, self.master)
        self.assertIn("82 of 424", self.master)
        self.assertIn("full-field censuses are not uniformly", self.master)
        self.assertIn("AlphaFold-generalised blind parity", self.master)
        self.assertIn("empirical validation is `NOT_RUN`", self.master)
        self.assertIn("deployment is `NOT_AUTHORIZED`", self.master)

    def test_complete_claim_inventory_matches_authority(self) -> None:
        expected = self.inventory["claim_ledger"]
        actual = self.claim_json["totals"]
        self.assertEqual(actual["claim_count"], expected["claim_count"], 2751)
        self.assertEqual(actual["candidate_count"], expected["candidate_count"], 892246)
        self.assertEqual(actual["survivor_count"], expected["survivor_count"], 2751)
        self.assertEqual(actual["control_count"], expected["control_count"], 11004)
        self.assertEqual(len(self.claim_json["claims"]), 2751)
        self.assertEqual(
            [row["claim_id"] for row in self.claim_json["claims"]],
            [row["claim_id"] for row in expected["claims"]],
        )
        required_fields = {
            "branch",
            "candidate_count",
            "candidate_census_sha256",
            "certificate_sha256",
            "claim_id",
            "closure_status",
            "control_count",
            "controls_sha256",
            "dependencies",
            "elimination_receipt_sha256",
            "external_status",
            "model_admitted",
            "receipt_file_sha256",
            "registered_receipt_id",
            "statement",
            "title",
            "unique_survivor_count",
        }
        for row in self.claim_json["claims"]:
            self.assertTrue(required_fields.issubset(row), row["claim_id"])

    def test_freeze_matches_built_files_and_active_papers(self) -> None:
        self.assertEqual(self.freeze["status"], "PASS_LOCAL_BUILD")
        self.assertEqual(self.freeze["failure_count"], 0)
        self.assertTrue(self.freeze["remote_publication_authorised"])
        self.assertFalse(self.freeze["protected_authority_edited"])
        self.assertEqual(self.freeze["master"]["master"]["sha256"], digest(MASTER))
        self.assertEqual(
            self.freeze["claim_inventory_markdown"]["sha256"], digest(CLAIM_MD)
        )
        self.assertEqual(
            self.freeze["claim_inventory_json"]["sha256"], digest(CLAIM_JSON)
        )
        self.assertEqual(len(self.freeze["active_papers"]), 17)
        self.assertTrue(
            all(row["identity_match"] for row in self.freeze["active_papers"])
        )
        self.assertEqual(len(self.freeze["audit_volumes"]), 17)
        self.assertTrue(all(self.freeze["invariants"].values()))

    def test_status_and_evidence_language_is_preserved(self) -> None:
        required_phrases = [
            "development-observed",
            "post-target",
            "adverse",
            "null",
            "failed source transport",
            "unavailable",
            "unresolved",
            "structural correspondence",
            "exact numerical correspondence",
            "compatibility",
            "current-evidence closure",
            "extension openness",
        ]
        master_casefolded = self.master.casefold()
        for phrase in required_phrases:
            self.assertIn(phrase.casefold(), master_casefolded, phrase)

    def test_publication_authority_and_licences(self) -> None:
        self.assertGreaterEqual(self.master.count("Maria Smith"), 10)
        self.assertIn("Ernos Labs", self.master)
        self.assertIn("Creative Commons Attribution 4.0 International", self.master)
        self.assertIn("Apache License 2.0", self.master)
        self.assertIn("authorised first standalone V3 preliminary publication", self.master)

    def test_new_standalone_v3_publication_identity(self) -> None:
        self.assertEqual(self.freeze["proposed_version"], "0.1.0")
        self.assertEqual(
            self.freeze["publication_operation"],
            "create_new_standalone_v3_record",
        )
        self.assertIsNone(self.freeze["concept_doi"])
        self.assertEqual(self.freeze["concept_record_id"], 21717583)
        self.assertEqual(self.freeze["zenodo_draft_id"], 21717584)
        self.assertEqual(self.freeze["version_doi"], "10.5281/zenodo.21717584")
        self.assertEqual(
            self.freeze["historical_pre_v3_concept_doi"],
            "10.5281/zenodo.21182468",
        )
        self.assertIn("**Standalone version:** 0.1.0", self.master)
        self.assertIn("new standalone V3 Zenodo lineage", self.master)
        self.assertIn("historical V2 identity only", self.master)
        self.assertNotIn("**Existing ToE concept DOI:**", self.master)
        self.assertNotIn("same-concept v7", self.master.casefold())

    def test_no_old_generated_claim_heading_defect(self) -> None:
        malformed = re.findall(r"(?m)^# SFT-[A-Z0-9-]+$", self.master)
        self.assertEqual(malformed, [])
        self.assertNotRegex(self.master, r"(?m)^# (?!The Smithian Fold Theory of Everything$).+")

    def test_no_editorial_placeholders_or_known_template_defects(self) -> None:
        forbidden = [
            "TODO",
            "TBD",
            "FIXME",
            "INSERT DOI",
            "lorem ipsum",
            "not separately recorded",
            ".. ",
        ]
        for text in forbidden:
            self.assertNotIn(text, self.master, text)


if __name__ == "__main__":
    unittest.main()
