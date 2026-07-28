"""Focused tests for the Consciousness and Cognitive Science foundation."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.consciousness_cognitive_science.empirical_program import CONSCIOUSNESS_SPECS, validate_external_evidence, validate_pre_source_seal
from sft.consciousness_cognitive_science.generated_law import candidate_forms, unique_survivor
from sft.consciousness_cognitive_science.obligations import CONSCIOUSNESS_OBLIGATIONS, FAMILY_COUNTS, FAMILY_ORDER
from sft.consciousness_cognitive_science.structural_model import structural_witnesses


ROOT = Path(__file__).resolve().parents[1]


class ConsciousnessFoundationTests(unittest.TestCase):
    def test_inventory_and_family_coverage(self) -> None:
        self.assertEqual(len(CONSCIOUSNESS_OBLIGATIONS), 72)
        self.assertEqual(tuple(FAMILY_COUNTS), FAMILY_ORDER)
        self.assertEqual(sum(FAMILY_COUNTS.values()), 72)

    def test_exact_structural_witnesses(self) -> None:
        witnesses = structural_witnesses()
        self.assertTrue(witnesses)
        self.assertTrue(all(witnesses.values()))

    def test_every_claim_enumerates_one_survivor(self) -> None:
        self.assertEqual(len(CONSCIOUSNESS_SPECS), 72)
        for spec in CONSCIOUSNESS_SPECS:
            forms = candidate_forms(spec.blueprint)
            self.assertEqual(len(forms), 256)
            self.assertEqual(len(set(forms)), 256)
            self.assertEqual("__".join(unique_survivor(spec.blueprint)), spec.exact_result)

    def test_pre_source_seal_and_external_evidence(self) -> None:
        self.assertEqual(validate_pre_source_seal(ROOT), "sha256:d7fb898ebeac6df5bde21e87fb6ee4a37e7b7b1dbd4f38b825c89e39f5708d71")
        audit, targets = validate_external_evidence(ROOT)
        self.assertEqual(audit["registered_feature_count"], 61)
        self.assertEqual(audit["present_feature_count"], 58)
        self.assertEqual(audit["absent_feature_count"], 3)
        self.assertEqual(targets["passed_claim_count"], 72)
        self.assertEqual(targets["unresolved_claim_count"], 0)

    def test_receipt_backed_admissions_and_non_substitution(self) -> None:
        census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        rows = [row for row in census if row.get("branch") == "consciousness_cognitive_science"]
        self.assertEqual([row["claim_id"] for row in rows], [row.claim_id for row in CONSCIOUSNESS_OBLIGATIONS])
        for row in rows:
            certificate = json.loads((ROOT / "claims" / row["claim_id"] / "certificate.json").read_text(encoding="utf-8"))
            self.assertEqual(certificate["engine_receipt_hash"], row["receipt_hash"])
            self.assertFalse(certificate["phenomenal_occurrence_directly_observed_by_third_person"])
            self.assertFalse(certificate["formal_structure_relabelled_as_empirical_phenomenal_fact"])


if __name__ == "__main__":
    unittest.main()
