from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.chemistry.obligations import OBLIGATIONS, SUBBRANCH_ORDER, validate_inventory
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent


class ChemistryInventoryTests(unittest.TestCase):
    def test_inventory_is_complete_and_dependency_ordered(self) -> None:
        validate_inventory()
        self.assertEqual(tuple(dict.fromkeys(row.subbranch for row in OBLIGATIONS)), SUBBRANCH_ORDER)
        self.assertEqual(len({row.claim_id for row in OBLIGATIONS}), len(OBLIGATIONS))
        self.assertTrue(all(row.external_source_ids for row in OBLIGATIONS))

    def test_every_external_source_is_registered_and_byte_sealed(self) -> None:
        registry = json.loads(
            (ROOT / "experiments/external_sources/chemistry/authoritative_sources.json").read_text(encoding="utf-8")
        )
        sources = {row["source_id"]: row for row in registry["sources"]}
        self.assertFalse({source for row in OBLIGATIONS for source in row.external_source_ids} - set(sources))
        for source in sources.values():
            self.assertEqual(hash_file(ROOT / source["snapshot_path"]), source["snapshot_hash"])

    def test_frozen_inventory_has_no_silent_omission(self) -> None:
        frozen = json.loads((ROOT / "publications/inventories/chemistry.json").read_text(encoding="utf-8"))
        self.assertTrue(frozen["inventory_frozen"])
        self.assertEqual(frozen["required_claim_count"], len(OBLIGATIONS))
        self.assertEqual(frozen["required_claim_ids"], [row.claim_id for row in OBLIGATIONS])
        self.assertEqual(frozen["unclassified_obligations"], [])
        self.assertEqual(frozen["frontier_obligations"], [])
        self.assertEqual(len(frozen["unobserved_prediction_targets"]), 3)


if __name__ == "__main__":
    unittest.main()
