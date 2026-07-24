from pathlib import Path
import unittest

from sft.physics.sector_inventory_validation_v1 import anchor_record


class SectorInventoryValidationTests(unittest.TestCase):
    def test_pdg_anchor_record(self) -> None:
        record = anchor_record(Path(__file__).resolve().parents[1])
        self.assertTrue(record["anchors_pass"])
        self.assertTrue(record["standing_predictions_retained"])


if __name__ == "__main__":
    unittest.main()
