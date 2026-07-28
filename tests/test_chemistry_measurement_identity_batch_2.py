from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.generated_law import BlindExternalChemistryValidator
from sft.chemistry.measurement_identity_batch_2 import (
    MEASUREMENT_IDENTITY_BATCH_2_SPECS,
    OBSERVATION_REGISTRY_PATH,
    SOURCE_RECORDS,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryMeasurementIdentityBatchTwoTests(unittest.TestCase):
    def test_batch_closes_the_registered_measurement_identity_ids(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in MEASUREMENT_IDENTITY_BATCH_2_SPECS),
            (
                "SFT-CHEM-MEAS-AMOUNT-001",
                "SFT-CHEM-MEAS-FORMULA-001",
                "SFT-CHEM-MEAS-NOMENCLATURE-001",
                "SFT-CHEM-MEAS-UNCERTAINTY-001",
                "SFT-CHEM-MEAS-TRACEABILITY-001",
            ),
        )

    def test_each_content_specific_grammar_is_exhaustive_and_unique(self) -> None:
        for spec in MEASUREMENT_IDENTITY_BATCH_2_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(identity == survivor_id(spec) for identity in identities), 1)
            self.assertEqual(len({axis.key for axis in spec.dimensions}), 8)

    def test_batch_targets_are_source_bound_without_observed_content(self) -> None:
        source_registry = json.loads(
            (ROOT / "experiments/external_sources/chemistry/authoritative_sources.json").read_text(
                encoding="utf-8"
            )
        )
        official = {row["source_id"]: row for row in source_registry["sources"]}
        for spec in MEASUREMENT_IDENTITY_BATCH_2_SPECS:
            self.assertEqual(spec.observation_registry_path, OBSERVATION_REGISTRY_PATH)
            for target in spec.target_rows:
                self.assertFalse(hasattr(target, "observed_label"))
                self.assertEqual(target.snapshot_hash, SOURCE_RECORDS[target.source_id]["snapshot_hash"])
                self.assertEqual(target.snapshot_hash, official[target.source_id]["snapshot_hash"])
                self.assertEqual(hash_file(ROOT / target.snapshot_path), target.snapshot_hash)

    def test_post_seal_source_reconstruction_and_unfavorable_control_pass(self) -> None:
        for spec in MEASUREMENT_IDENTITY_BATCH_2_SPECS:
            sealed = SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "test-seal")))
            result = BlindExternalChemistryValidator(ROOT, spec).validate(sealed)
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_first_admission_batch_authority_files_remain_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/generated_law.py": "sha256:678de1061dcd4b4a24deefd7757045729d89677d6170bd907cde70bc9ca2e15a",
            "sft/chemistry/catalog.py": "sha256:90750420738638bdadd783f0fb83bc667ee414cc48036e5cdc2f9a2a61089fd6",
            "sft/chemistry/obligations.py": "sha256:b502afe57640149166b4ca69b433d02b3361155eb624f9af8cb8918f77ac0ad7",
            "experiments/external_sources/chemistry/observations.json": "sha256:3cc52c9bc35d2625b26940a92b9f5f26b1a75f58e8f7493b224e033c94464c62",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
