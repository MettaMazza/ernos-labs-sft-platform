from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.chemistry.prediction_prerequisite_audit import (
    capacity_witnesses,
    run_prerequisite_audit,
)
from sft.engine.exact import PositiveCount


ROOT = Path(__file__).resolve().parent.parent


class ChemistryPredictionPrerequisiteAuditTests(unittest.TestCase):
    def test_preserved_prediscriminator_dependencies_do_not_select_one_capacity_family(self) -> None:
        linear, doubled = capacity_witnesses(PositiveCount(4))
        self.assertNotEqual(linear, doubled)
        self.assertEqual(tuple(value.value for value in linear), (2, 4, 6, 8))
        self.assertEqual(tuple(value.value for value in doubled), (2, 4, 8, 16))

    def test_preserved_prediscriminator_audit_retains_all_three_then_unresolved_ids(self) -> None:
        audit = run_prerequisite_audit()
        self.assertFalse(audit.admissible)
        self.assertFalse(audit.unique_subshell_capacity)
        self.assertFalse(audit.unique_nuclear_closure)
        self.assertFalse(audit.forced_terminal_coordinate)
        self.assertEqual(
            audit.unresolved_claim_ids,
            (
                "SFT-CHEM-PRED-G-BLOCK-001",
                "SFT-CHEM-PRED-SMITHIUM-001",
                "SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
            ),
        )

    def test_later_discriminator_claims_and_predictions_are_now_admitted(self) -> None:
        admitted = {
            row["claim_id"]
            for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        }
        self.assertTrue(
            {
                "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
                "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
                "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
                "SFT-CHEM-PRED-G-BLOCK-001",
                "SFT-CHEM-PRED-SMITHIUM-001",
                "SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
            }
            <= admitted
        )


if __name__ == "__main__":
    unittest.main()
