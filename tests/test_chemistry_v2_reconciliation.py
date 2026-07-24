from __future__ import annotations

import unittest

from sft.chemistry.v2_reconciliation import (
    V2_CHEMISTRY_QUESTIONS,
    validate_v2_chemistry_reconciliation,
)


class ChemistryV2ReconciliationTests(unittest.TestCase):
    def test_question_inventory_is_valid(self) -> None:
        validate_v2_chemistry_reconciliation()

    def test_known_chemistry_steps_are_present(self) -> None:
        self.assertEqual(
            {50, 77, 78, 112, 142, 144, 156, 157, 167, 176, 249, 266, 267, 293, 294},
            {row.step for row in V2_CHEMISTRY_QUESTIONS},
        )

    def test_smithium_prerequisites_are_explicit_and_resolved(self) -> None:
        smithium = next(row for row in V2_CHEMISTRY_QUESTIONS if row.step == 293)
        self.assertEqual(smithium.prerequisite_gap, "")
        self.assertIn("SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", smithium.prerequisite_claim_ids)
        self.assertIn("SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001", smithium.prerequisite_claim_ids)


if __name__ == "__main__":
    unittest.main()
