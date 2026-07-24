from pathlib import Path
from types import SimpleNamespace
import unittest
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.chemistry.redox_batch_1 import REDOX_BATCH_1_SPECS, validate_pre_source_seal
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import candidate_rows, survivor_id
ROOT = Path(__file__).resolve().parent.parent
class ChemistryRedoxBatchOneTests(unittest.TestCase):
    def test_five_registered_obligations(self):
        self.assertEqual(len(REDOX_BATCH_1_SPECS), 5)
    def test_pre_source_seal(self):
        validate_pre_source_seal()
    def test_each_grammar_has_256_forms_and_one_survivor(self):
        for spec in REDOX_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            self.assertEqual(len(rows), 256)
            self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)
    def test_official_source_sets_match_only_after_seal(self):
        for spec in REDOX_BATCH_1_SPECS:
            result = BlindMultiSourceAuthorityValidator(ROOT, spec).validate(SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "redox-test"))))
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])
if __name__ == "__main__":
    unittest.main()
