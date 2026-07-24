from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.catalog import CHEMISTRY_SPECS, PENDING_CHEMISTRY_CLAIM_IDS
from sft.chemistry.generated_law import BlindExternalChemistryValidator
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryCatalogTests(unittest.TestCase):
    def test_only_content_specific_ready_specs_enter_catalog(self) -> None:
        self.assertEqual(len(CHEMISTRY_SPECS), 3)
        self.assertEqual(len(PENDING_CHEMISTRY_CLAIM_IDS), 83)
        self.assertFalse({spec.claim_id for spec in CHEMISTRY_SPECS} & set(PENDING_CHEMISTRY_CLAIM_IDS))

    def test_each_ready_grammar_is_complete_and_unique(self) -> None:
        for spec in CHEMISTRY_SPECS:
            rows = candidate_rows(spec)
            identifiers = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identifiers)), 256)
            self.assertEqual(sum(identifier == survivor_id(spec) for identifier in identifiers), 1)
            self.assertEqual(len({dimension.key for dimension in spec.dimensions}), 8)

    def test_target_content_is_absent_from_derivation_references(self) -> None:
        for spec in CHEMISTRY_SPECS:
            for target in spec.target_rows:
                self.assertFalse(hasattr(target, "observed_label"))
                self.assertTrue(target.snapshot_hash.startswith("sha256:"))

    def test_source_derived_correspondence_and_unfavorable_control_pass(self) -> None:
        sealed = SimpleNamespace(seal_hash=sha256_identity("Chemistry test derivation seal"))
        for spec in CHEMISTRY_SPECS:
            result = BlindExternalChemistryValidator(ROOT, spec).validate(sealed)
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])


if __name__ == "__main__":
    unittest.main()
