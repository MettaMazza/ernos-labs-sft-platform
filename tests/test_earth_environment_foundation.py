"""Focused tests for the Earth and Environmental Sciences foundation."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest

from sft.earth_environment.empirical_program import EARTH_SPECS, validate_external_evidence, validate_pre_source_seal
from sft.earth_environment.generated_law import candidate_forms, unique_survivor
from sft.earth_environment.obligations import EARTH_ENVIRONMENT_OBLIGATIONS, FAMILY_ORDER
from sft.earth_environment.structural_model import structural_witnesses


ROOT = Path(__file__).resolve().parents[1]


class EarthEnvironmentFoundationTests(unittest.TestCase):
    def test_inventory_and_family_coverage(self) -> None:
        self.assertEqual(len(EARTH_ENVIRONMENT_OBLIGATIONS), 74)
        self.assertEqual(tuple(dict.fromkeys(row.family for row in EARTH_ENVIRONMENT_OBLIGATIONS)), FAMILY_ORDER)
        counts = Counter(row.family for row in EARTH_ENVIRONMENT_OBLIGATIONS)
        self.assertEqual(sum(counts.values()), 74)
        self.assertEqual(len(counts), 12)

    def test_exact_structural_witnesses(self) -> None:
        witnesses = structural_witnesses()
        self.assertTrue(witnesses)
        self.assertTrue(all(witnesses.values()))

    def test_every_claim_enumerates_one_survivor(self) -> None:
        self.assertEqual(len(EARTH_SPECS), 74)
        for spec in EARTH_SPECS:
            forms = candidate_forms(spec.blueprint)
            self.assertEqual(len(forms), 256)
            self.assertEqual(len(set(forms)), 256)
            self.assertEqual("__".join(row.name for row in unique_survivor(spec.blueprint)), spec.exact_result)

    def test_pre_source_seal_and_external_evidence(self) -> None:
        self.assertEqual(validate_pre_source_seal(ROOT), "sha256:c741b6b227098e41568c29fa05a4c7261152d2a3838b410620954e7c17bfb0cc")
        audit, targets, _ = validate_external_evidence(ROOT)
        self.assertEqual(audit["registered_feature_count"], 91)
        self.assertEqual(audit["present_feature_count"], 67)
        self.assertEqual(audit["absent_feature_count"], 24)
        self.assertEqual(targets["passed_claim_count"], 74)
        self.assertEqual(targets["unresolved_claim_count"], 0)

    def test_receipts_and_evidence_non_substitution(self) -> None:
        census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        rows = [row for row in census if row.get("branch") == "earth_environment"]
        self.assertEqual([row["claim_id"] for row in rows], [row.claim_id for row in EARTH_ENVIRONMENT_OBLIGATIONS])
        for row in rows:
            certificate = json.loads((ROOT / "claims" / row["claim_id"] / "certificate.json").read_text(encoding="utf-8"))
            self.assertEqual(certificate["engine_receipt_hash"], row["receipt_hash"])
            self.assertFalse(certificate["external_evidence_selected_survivor"])
            self.assertFalse(certificate["formal_structure_relabelled_as_direct_measurement"])
            self.assertFalse(certificate["model_or_forecast_relabelled_as_observation"])

    def test_earthquake_adverse_and_holdout_are_both_preserved(self) -> None:
        target = json.loads((ROOT / "experiments/earth_environment/claim_specific_external_targets.json").read_text(encoding="utf-8"))
        numeric = next(row for row in target["targets"] if row["claim_id"] == "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001")["numeric_comparison"]
        self.assertFalse(numeric["first_mixed_catalog_result"]["passed"])
        self.assertFalse(numeric["first_adverse_result_reclassified"])
        self.assertTrue(numeric["independent_homogeneous_holdout"]["passed"])


if __name__ == "__main__":
    unittest.main()
