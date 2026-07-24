from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class V1ObservationCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.census = json.loads(
            (ROOT / "audits/v1_theorem_manifest_observation_census.json").read_text()
        )

    def test_complete_bound_manifest_is_registered(self) -> None:
        self.assertEqual(self.census["source_row_count"], 356)
        self.assertEqual(
            self.census["source_kind_counts"],
            {"DEF": 3, "E": 334, "OBS": 4, "THM": 15},
        )
        self.assertEqual(len({row["v1_claim_id"] for row in self.census["rows"]}), 356)

    def test_unresolved_v1_results_block_until_explicitly_disposed(self) -> None:
        self.assertEqual(self.census["mapped_row_count"], 9)
        self.assertEqual(self.census["unmapped_row_count"], 347)
        self.assertEqual(self.census["same_strength_closed_row_count"], 4)
        self.assertEqual(self.census["same_strength_open_row_count"], 352)
        self.assertTrue(self.census["status"].startswith("open_blocking"))

    def test_closed_value_rows_retain_engine_receipts(self) -> None:
        m15 = next(row for row in self.census["rows"] if row["v1_claim_id"] == "M15")
        n8b = next(row for row in self.census["rows"] if row["v1_claim_id"] == "N8b")
        g11 = next(row for row in self.census["rows"] if row["v1_claim_id"] == "G11")
        n1e = next(row for row in self.census["rows"] if row["v1_claim_id"] == "N1e")
        self.assertTrue(m15["same_strength_disposition"]["closed"])
        self.assertTrue(n8b["same_strength_disposition"]["closed"])
        self.assertTrue(g11["same_strength_disposition"]["closed"])
        self.assertTrue(n1e["same_strength_disposition"]["closed"])
        self.assertEqual(
            n8b["same_strength_disposition"]["receipt_hash"],
            "sha256:38b06863d5a59f8f8ea17fee7a0a1d5ff1fdcd0c6f7b9de3e9f635705d4f8cc2",
        )
        self.assertEqual(
            g11["same_strength_disposition"]["receipt_hash"],
            "sha256:d4ce8d8568e94b5032fc65633d024aaa7cba6365e6d88217c61ec9a388153e88",
        )
        self.assertEqual(
            n1e["same_strength_disposition"]["receipt_hash"],
            "sha256:ec8cf537a7460687e1ca3d1c9e5d1781b96b477e4c11f68d7c3208e82d3d1a66",
        )

    def test_observation_does_not_become_derivation_input(self) -> None:
        policy = self.census["policy"]
        self.assertTrue(policy["prior_results_are_observational_data"])
        self.assertFalse(policy["prior_answer_artifacts_may_enter_v3_derivation"])
        self.assertFalse(policy["prior_observation_may_select_v3_candidate_or_survivor"])


if __name__ == "__main__":
    unittest.main()
