import json
from pathlib import Path
import unittest

from sft.astronomy_cosmology.generated_law import ASTRONOMY_BLUEPRINTS, candidate_forms, unique_survivor
from sft.astronomy_cosmology.structural_model import structural_witnesses

ROOT=Path(__file__).resolve().parents[1]

class AstronomyFoundationTests(unittest.TestCase):
    def test_inventory(self):
        self.assertEqual(len(ASTRONOMY_BLUEPRINTS),72)
        self.assertEqual(len({x.claim_id for x in ASTRONOMY_BLUEPRINTS}),72)
    def test_candidates_and_survivors(self):
        self.assertEqual(sum(len(candidate_forms(x)) for x in ASTRONOMY_BLUEPRINTS),18432)
        self.assertTrue(all(len(unique_survivor(x))==8 for x in ASTRONOMY_BLUEPRINTS))
    def test_structural_witnesses(self):
        self.assertTrue(all(structural_witnesses().values()))
    def test_external_rows(self):
        x=json.loads((ROOT/"experiments/astronomy_cosmology/external_targets.json").read_text())
        self.assertEqual((x["claim_count"],x["passed_claim_count"],x["unresolved_claim_count"]),(72,72,0))
        self.assertTrue(x["first_btfr_adverse_preserved"])
        self.assertFalse(x["first_btfr_adverse_reclassified"])
    def test_receipts(self):
        claims=json.loads((ROOT/"census/claims.json").read_text())["claims"]
        admitted={x["claim_id"] for x in claims if x.get("model_admitted") is True}
        self.assertTrue({x.claim_id for x in ASTRONOMY_BLUEPRINTS} <= admitted)
    def test_seals_named(self):
        x=json.loads((ROOT/"experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json").read_text())
        self.assertEqual(x["required_claim_count"],72); self.assertEqual(x["candidate_count"],18432)

if __name__=="__main__": unittest.main()
