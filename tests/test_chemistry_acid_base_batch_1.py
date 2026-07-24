from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.acid_base_batch_1 import ACID_BASE_BATCH_1_SPECS, validate_pre_source_seal
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryAcidBaseBatchOneTests(unittest.TestCase):
    def test_batch_closes_five_acid_base_obligations(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in ACID_BASE_BATCH_1_SPECS),
            (
                "SFT-CHEM-AB-ACID-BASE-001",
                "SFT-CHEM-AB-PROTON-TRANSFER-001",
                "SFT-CHEM-AB-LEWIS-001",
                "SFT-CHEM-AB-AMPHOTERIC-001",
                "SFT-CHEM-AB-BUFFER-001",
            ),
        )

    def test_pre_source_seal_binds_target_blind_derivation(self) -> None:
        validate_pre_source_seal()
        self.assertEqual(
            hash_file(ROOT / "sft/chemistry/acid_base_derivation.py"),
            "sha256:50e328d932a018c7895f07d723b31076f96e99529b38504df1490ccaa764008c",
        )

    def test_each_grammar_exhausts_256_forms_with_one_survivor(self) -> None:
        for spec in ACID_BASE_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(row == survivor_id(spec) for row in identities), 1)

    def test_post_seal_authority_rows_and_tampered_controls_pass(self) -> None:
        for spec in ACID_BASE_BATCH_1_SPECS:
            result = BlindMultiSourceAuthorityValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "acid-base-test-seal")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_registered_support_documents_are_byte_frozen(self) -> None:
        expected = {
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/B00744.json": "sha256:243711708fadda8ebb2f5acfc7108d5b88205c2c40adc1ef9129809ac16db3a9",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/B00745.json": "sha256:47cc7a6d02ebfcc0025656b3ef92292a02ddd5f303c811d440f66eddcac0557f",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/C01266.json": "sha256:1ac0d6138e316d6230d10b2e7f99d4837175fcb640e824a8cb2249100221a504",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/P04915.json": "sha256:72d9b1431f3daa6b0190094d8400bc73b31e786b7d69b4052632297b4b709d33",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/L03508.json": "sha256:9fa013b12d6d0e3f305883a0db53dac7484e292e0288e2c3d0ba9625cfb2011c",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/L03511.json": "sha256:ffa4ee695efef5da476dd1ab4f787c5854a46009a58bb9fced3f1c113aa284df",
            "experiments/external_sources/chemistry/snapshots/goldbook-terms/A00306.json": "sha256:70ab5021338400d9f02cbecc5c45b9f4271792e919d880aafff81684739022ab",
            "experiments/external_sources/chemistry/snapshots/iupac-didac-buffer-e15-extract.html": "sha256:570a91d1a7de35b22a8469c117f10af9e4bed3012ae61f54362fe45534b3d01e",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
