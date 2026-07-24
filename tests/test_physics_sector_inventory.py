import unittest

from sft.physics.sector_inventory_law_v1 import SPEC
from sft.physics.structural_constants import candidate_rows


class SectorInventoryTests(unittest.TestCase):
    def test_complete_inventory_grammar(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)


if __name__ == "__main__":
    unittest.main()
