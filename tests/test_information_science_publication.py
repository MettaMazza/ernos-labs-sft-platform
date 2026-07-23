import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_information_science_publication",
    ROOT / "tools/verify_information_science_publication.py",
)
assert SPEC and SPEC.loader
publication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publication)


class InformationSciencePublicationTests(unittest.TestCase):
    def test_frozen_inventory_identity_is_valid(self):
        inventory = publication.load_inventory()
        self.assertTrue(inventory.frozen)
        self.assertEqual(len(inventory.required_claim_ids), 12)
        self.assertEqual(inventory.unclassified_obligations, ())
        self.assertEqual(inventory.frontier_obligations, ())

    def test_evidence_map_covers_every_claim_in_order(self):
        inventory = publication.load_inventory()
        evidence_map = publication.build_evidence_map()
        publication.evidence_map_controls(evidence_map, inventory)
        self.assertEqual(
            tuple(entry["claim_id"] for entry in evidence_map["claims"]),
            inventory.required_claim_ids,
        )
        self.assertEqual(sum(entry["candidate_count"] for entry in evidence_map["claims"]), 11776)
        self.assertTrue(evidence_map["publication_action_authorized"])

    def test_missing_claim_and_missing_authorization_are_detected(self):
        inventory = publication.load_inventory()
        evidence_map = publication.build_evidence_map()
        missing = copy.deepcopy(evidence_map)
        missing["claims"].pop()
        with self.assertRaises(ValueError):
            publication.evidence_map_controls(missing, inventory)
        falsely_unauthorized = copy.deepcopy(evidence_map)
        falsely_unauthorized["publication_action_authorized"] = False
        with self.assertRaises(ValueError):
            publication.evidence_map_controls(falsely_unauthorized, inventory)

    def test_written_bundle_passes_local_publication_gate(self):
        result = publication.verify_written_bundle()
        self.assertEqual(result["claim_count"], 12)
        self.assertEqual(result["candidate_count"], 11776)


if __name__ == "__main__":
    unittest.main()
