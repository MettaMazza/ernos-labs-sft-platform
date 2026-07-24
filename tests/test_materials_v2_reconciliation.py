from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.materials.v2_reconciliation import V2_MATERIALS_QUESTIONS, validate_v2_materials_reconciliation


ROOT = Path(__file__).resolve().parent.parent


class MaterialsV2ReconciliationTests(unittest.TestCase):
    def test_question_inventory_is_complete_and_valid(self) -> None:
        validate_v2_materials_reconciliation()
        self.assertEqual(
            {47, 49, 52, 54, 72, 74, 75, 133, 137, 143, 193, 291},
            {row.step for row in V2_MATERIALS_QUESTIONS},
        )

    def test_every_mapped_v3_claim_is_model_admitted(self) -> None:
        admitted = {
            row["claim_id"]
            for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        }
        required = {
            claim_id for row in V2_MATERIALS_QUESTIONS for claim_id in row.required_v3_claim_ids
        }
        self.assertEqual(required - admitted, set())

    def test_mixed_step_does_not_hide_astrophysics(self) -> None:
        mixed = next(row for row in V2_MATERIALS_QUESTIONS if row.step == 291)
        self.assertIn("Astronomy and Cosmology", mixed.routed_remainder)


if __name__ == "__main__":
    unittest.main()
