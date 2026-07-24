from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "census/lineage_reconciliation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class LineageReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text())

    def test_every_bound_source_matches_its_recorded_hash_when_present(self) -> None:
        for source in self.registry["source_custody"]:
            path = Path(source["path"])
            if not path.exists():
                continue
            with self.subTest(source_id=source["source_id"]):
                self.assertEqual(sha256(path), source["sha256"])

    def test_authoritative_v2_has_every_step_once_and_in_order(self) -> None:
        source = next(
            row
            for row in self.registry["source_custody"]
            if row["source_id"] == "SFT-V2-ONE-FOLD-MASTER-407"
        )
        source_path = Path(source["path"])
        if not source_path.exists():
            self.skipTest("authoritative prior corpus is not installed in this clean clone")
        text = source_path.read_text()
        headings = re.findall(r"^### Step (\d+) .+$", text, flags=re.MULTILINE)
        self.assertEqual([int(value) for value in headings], list(range(1, 408)))

        ordered_lines = "\n".join(
            re.findall(r"^### Step \d+ .+$", text, flags=re.MULTILINE)
        ) + "\n"
        heading_hash = hashlib.sha256(ordered_lines.encode()).hexdigest()
        self.assertEqual(heading_hash, source["ordered_heading_manifest_sha256"])

    def test_missing_lineage_work_is_blocking_not_historical_completion(self) -> None:
        law = self.registry["completion_law"]
        self.assertTrue(law["historical_status_is_not_completion"])
        self.assertTrue(law["branch_inventory_boundaries_cannot_hide_lineage_obligations"])
        self.assertEqual(
            law["missing_mapping_status"],
            "blocking_v3_reconstruction_required",
        )
        self.assertFalse(self.registry["v2_step_census"]["current_complete_step_to_claim_map"])
        self.assertEqual(self.registry["status"], "open_blocking")
        prior = json.loads((ROOT / "prior-work-ledger/manifest.json").read_text())
        self.assertTrue(prior["mandatory_reconciliation_authority"])
        self.assertTrue(
            all(row["mandatory_reconciliation_authority"] for row in prior["entries"])
        )

    def test_named_consequence_groups_cover_the_requested_high_risk_omissions(self) -> None:
        rows = {row["group_id"]: row for row in self.registry["named_consequence_groups"]}
        required = {
            "vacuum_zero_point_and_vacuum_floor",
            "vacuum_energy_extraction_and_inertia_engineering",
            "additional_forces_and_unification",
            "elements_nuclear_structure_and_island_of_stability",
            "particle_neutrino_dark_sector_and_complete_inventory",
            "consciousness_qualia_self_and_subjectivity",
            "extreme_gravity_information_and_nonstandard_spacetime",
            "life_biology_medicine_and_collective_systems",
            "famous_mathematical_scientific_and_computational_closures",
        }
        self.assertEqual(set(rows), required)
        self.assertIn("specific qualia as stable coupled attractor including the red-of-red case", rows["consciousness_qualia_self_and_subjectivity"]["required_results"])
        self.assertIn("net extractable-work accounting over a complete returned cycle", rows["vacuum_energy_extraction_and_inertia_engineering"]["required_results"])
        self.assertIn("Smithium at Z=126 N=184 A=310", rows["elements_nuclear_structure_and_island_of_stability"]["required_results"])
        self.assertIn("83 gauge carriers", rows["particle_neutrino_dark_sector_and_complete_inventory"]["required_results"])
        self.assertEqual(
            rows["elements_nuclear_structure_and_island_of_stability"]["v3_status"],
            "closed_current_v3_standard",
        )
        for group_id, row in rows.items():
            if group_id != "elements_nuclear_structure_and_island_of_stability":
                self.assertTrue(row["v3_status"].startswith("blocking_"))

    def test_chemistry_publication_is_fail_closed(self) -> None:
        state = self.registry["publication_state"]
        self.assertTrue(state["chemistry_paper_exists_in_publications_current"])
        self.assertTrue(state["chemistry_release_exists_in_output_release"])
        self.assertTrue(state["chemistry_github_release_observed"])
        self.assertTrue(state["chemistry_zenodo_record_observed"])
        self.assertTrue(state["chemistry_publication_permitted"])
        paper_root = ROOT / "publications/current/chemistry"
        self.assertTrue((paper_root / "FROM_FOLD_TO_CHEMISTRY.md").is_file())
        self.assertTrue((paper_root / "evidence_map.json").is_file())
        self.assertTrue((paper_root / "manifest.json").is_file())
        self.assertTrue((paper_root / "publication_receipt.json").is_file())
        release = json.loads((ROOT / "publication/chemistry_release.json").read_text())
        self.assertEqual(release["doi"], "10.5281/zenodo.21531455")
        self.assertTrue(all(release["public_verification"].values()))


if __name__ == "__main__":
    unittest.main()
