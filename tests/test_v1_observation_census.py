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

    def test_every_v1_result_blocks_until_explicitly_disposed(self) -> None:
        self.assertEqual(self.census["mapped_row_count"], 0)
        self.assertEqual(self.census["unmapped_row_count"], 356)
        self.assertTrue(self.census["status"].startswith("open_blocking"))

    def test_observation_does_not_become_derivation_input(self) -> None:
        policy = self.census["policy"]
        self.assertTrue(policy["prior_results_are_observational_data"])
        self.assertFalse(policy["prior_answer_artifacts_may_enter_v3_derivation"])
        self.assertFalse(policy["prior_observation_may_select_v3_candidate_or_survivor"])


if __name__ == "__main__":
    unittest.main()
