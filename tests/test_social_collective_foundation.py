import json
from pathlib import Path
import unittest

from sft.social_collective_systems.generated_law import SOCIAL_BLUEPRINTS, candidate_forms, unique_survivor
from sft.social_collective_systems.structural_model import structural_witnesses

ROOT = Path(__file__).resolve().parents[1]


class SocialCollectiveFoundationTests(unittest.TestCase):
    def test_inventory(self):
        self.assertEqual(len(SOCIAL_BLUEPRINTS), 72)
        self.assertEqual(len({x.claim_id for x in SOCIAL_BLUEPRINTS}), 72)

    def test_candidates_and_survivors(self):
        self.assertEqual(sum(len(candidate_forms(x)) for x in SOCIAL_BLUEPRINTS), 18432)
        self.assertTrue(all(len(unique_survivor(x)) == 8 for x in SOCIAL_BLUEPRINTS))

    def test_structural_witnesses(self):
        self.assertTrue(all(structural_witnesses().values()))

    def test_external_rows_and_epistemic_boundaries(self):
        document = json.loads((ROOT / "experiments/social_collective_systems/external_targets.json").read_text())
        self.assertEqual((document["claim_count"], document["passed_claim_count"], document["unresolved_claim_count"]), (72, 72, 0))
        self.assertTrue(document["all_adverse_absent_and_failed_rows_preserved"])
        self.assertFalse(document["credential_prestige_or_consensus_used_as_proof"])

    def test_receipts(self):
        claims = json.loads((ROOT / "census/claims.json").read_text())["claims"]
        admitted = {x["claim_id"] for x in claims if x.get("model_admitted") is True}
        self.assertTrue({x.claim_id for x in SOCIAL_BLUEPRINTS} <= admitted)

    def test_pre_source_seal(self):
        document = json.loads((ROOT / "experiments/sealed_predictions/social_collective_foundation_complete_pre_source.json").read_text())
        self.assertEqual(document["required_claim_count"], 72)
        self.assertEqual(document["candidate_count"], 18432)
        self.assertFalse(document["external_source_identities_selected"])


if __name__ == "__main__":
    unittest.main()
