from __future__ import annotations

import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.landauer_demon_empirical_v1 import SPEC


class LandauerEmpiricalTests(unittest.TestCase):
    def test_spec_and_complete_rows(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.target_rows), 4)

    def test_complete_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_scope_is_explicit(self) -> None:
        self.assertIn("long-cycle", SPEC.statement)
        self.assertIn("not equated", SPEC.statement)


if __name__ == "__main__":
    unittest.main()
