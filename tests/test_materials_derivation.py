"""Target-blind Materials derivation inventory and product checks."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.materials.derivation import MATERIALS_BLUEPRINTS, blueprint_candidate_ids
from sft.materials.obligations import MATERIALS_OBLIGATIONS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parent.parent


class MaterialsDerivationTests(unittest.TestCase):
    def test_complete_prediction_surface_is_pre_source_sealed(self) -> None:
        path = ROOT / "experiments/sealed_predictions/materials_complete_branch_pre_source.json"
        seal = json.loads(path.read_text(encoding="utf-8"))
        claimed_hash = seal.pop("sealed_payload_hash")
        self.assertEqual(claimed_hash, "sha256:da97a6cb6a001964a069b45a5a3698e7ea90f334a08d69c62bd09c46d8112035")
        self.assertEqual(sha256_identity(seal), claimed_hash)
        self.assertEqual(seal["required_claim_count"], len(MATERIALS_BLUEPRINTS))
        self.assertEqual(seal["candidate_count"], len(MATERIALS_BLUEPRINTS) * 256)
        prediction_set = tuple(
            (row.claim_id, row.exact_result, row.predicted_observation_label)
            for row in MATERIALS_BLUEPRINTS
        )
        self.assertEqual(seal["claim_prediction_set_hash"], sha256_identity(prediction_set))
        for path_key, hash_key in (
            ("inventory_path", "inventory_hash"),
            ("structural_counts_path", "structural_counts_hash"),
            ("derivation_path", "derivation_hash"),
        ):
            self.assertEqual(hash_file(ROOT / seal[path_key]), seal[hash_key])
        self.assertIs(seal["external_source_identities_selected"], False)
        self.assertIs(seal["external_target_content_opened"], False)

    def test_every_inventory_obligation_has_one_blueprint_in_order(self) -> None:
        self.assertEqual(
            tuple(row.claim_id for row in MATERIALS_BLUEPRINTS),
            tuple(row.claim_id for row in MATERIALS_OBLIGATIONS),
        )
        self.assertEqual(len(MATERIALS_BLUEPRINTS), 84)

    def test_each_blueprint_exhausts_256_forms_with_one_survivor(self) -> None:
        for blueprint in MATERIALS_BLUEPRINTS:
            with self.subTest(claim_id=blueprint.claim_id):
                candidates = blueprint_candidate_ids(blueprint)
                self.assertEqual(len(candidates), 256)
                self.assertEqual(len(set(candidates)), 256)
                self.assertEqual(sum(row == blueprint.exact_result for row in candidates), 1)

    def test_every_dependency_is_already_admitted(self) -> None:
        admitted = {
            row["claim_id"]
            for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        }
        missing = {
            dependency
            for blueprint in MATERIALS_BLUEPRINTS
            for dependency in blueprint.dependencies
            if dependency not in admitted
        }
        self.assertEqual(missing, set())

    def test_no_blueprint_has_axiom_parameter_or_external_target_field(self) -> None:
        for blueprint in MATERIALS_BLUEPRINTS:
            fields = set(blueprint.__dataclass_fields__)
            self.assertFalse({"axioms", "free_parameters", "target_rows", "source_id"} & fields)
            self.assertTrue(all(witness[2] for witness in blueprint.operational_witnesses))


if __name__ == "__main__":
    unittest.main()
