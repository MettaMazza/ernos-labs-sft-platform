from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.chemistry.stereochemistry_organic_polymer_batch_1 import (
    STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS,
    validate_pre_source_seal,
)
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class TestStereochemistryOrganicPolymerBatchOne(unittest.TestCase):
    def test_eight_obligations(self):
        self.assertEqual(len(STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS), 8)

    def test_pre_source_seal(self):
        validate_pre_source_seal()

    def test_unique_products(self):
        for spec in STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            self.assertEqual(len(rows), 256)
            self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)

    def test_post_seal_authority_and_control(self):
        for spec in STEREOCHEMISTRY_ORGANIC_POLYMER_BATCH_1_SPECS:
            result = BlindMultiSourceAuthorityValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "stereochemistry-organic-polymer-test")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])


if __name__ == "__main__":
    unittest.main()
