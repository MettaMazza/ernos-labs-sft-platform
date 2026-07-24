"""Complete Materials generated-law and blind-boundary tests."""

from __future__ import annotations

from pathlib import Path
import unittest

from sft.materials.generated_law import MATERIALS_SPECS, validate_pre_source_seal
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class MaterialsGeneratedLawTests(unittest.TestCase):
    def test_complete_catalog_is_bound_to_pre_source_seal(self) -> None:
        self.assertTrue(validate_pre_source_seal(ROOT).startswith("sha256:"))
        self.assertEqual(len(MATERIALS_SPECS), 84)

    def test_every_law_has_complete_product_and_one_survivor(self) -> None:
        for spec in MATERIALS_SPECS:
            with self.subTest(claim_id=spec.claim_id):
                rows = candidate_rows(spec)
                self.assertEqual(len(rows), 256)
                self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)
                self.assertEqual(spec.exact_result, survivor_id(spec))

    def test_every_binding_has_two_or_more_source_discriminators(self) -> None:
        from sft.materials.external_bindings import BINDING_BY_CLAIM

        for spec in MATERIALS_SPECS:
            self.assertGreaterEqual(len(BINDING_BY_CLAIM[spec.claim_id].requirements), 2)
            self.assertTrue(spec.source_ids)


if __name__ == "__main__":
    unittest.main()
