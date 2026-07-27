"""Foundational Medicine target-blind derivation and source-boundary tests."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.medicine.empirical_program import MEDICINE_SPECS, validate_pre_source_seal
from sft.medicine.external_bindings import BINDING_BY_CLAIM
from sft.medicine.generated_law import MEDICINE_BLUEPRINTS, candidate_forms, unique_survivor
from sft.medicine.obligations import FAMILY_ORDER, MEDICINE_OBLIGATIONS
from sft.medicine.sources import MEDICINE_AUTHORITY_SOURCES, source_corpus, validate_sources
from sft.medicine.structural_counts import diagnostic_table_certificate, exact_share, two_arm_outcome_certificate
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


class MedicineFoundationTests(unittest.TestCase):
    def test_complete_prediction_surface_is_pre_source_sealed(self) -> None:
        path = ROOT / "experiments/sealed_predictions/medicine_foundation_complete_pre_source.json"
        seal = json.loads(path.read_text(encoding="utf-8"))
        claimed = seal.pop("complete_branch_pre_source_seal_hash")
        self.assertEqual(claimed, "sha256:57b0813078b36814b831862db7e888601d8e1c1d2820f7429915431bf6066cd5")
        self.assertEqual(sha256_identity(seal), claimed)
        self.assertEqual(seal["required_claim_count"], 72)
        self.assertEqual(seal["candidate_count"], 18_432)
        for path_key, hash_key in (("inventory_path", "inventory_file_hash"), ("obligations_path", "obligations_hash"), ("generated_law_path", "generated_law_hash"), ("structural_counts_path", "structural_counts_hash")):
            self.assertEqual(hash_file(ROOT / seal[path_key]), seal[hash_key])
        self.assertIs(seal["external_source_identities_selected"], False)
        self.assertIs(seal["external_outcomes_opened"], False)

    def test_inventory_blueprints_and_specs_are_exactly_aligned(self) -> None:
        identities = tuple(row.claim_id for row in MEDICINE_OBLIGATIONS)
        self.assertEqual(identities, tuple(row.claim_id for row in MEDICINE_BLUEPRINTS))
        self.assertEqual(identities, tuple(row.claim_id for row in MEDICINE_SPECS))
        self.assertEqual(len(identities), 72)
        self.assertEqual(tuple(dict.fromkeys(row.family for row in MEDICINE_OBLIGATIONS)), FAMILY_ORDER)
        self.assertTrue(all(sum(row.family == family for row in MEDICINE_OBLIGATIONS) == 6 for family in FAMILY_ORDER))

    def test_every_blueprint_exhausts_256_forms_with_one_survivor(self) -> None:
        for blueprint in MEDICINE_BLUEPRINTS:
            with self.subTest(claim_id=blueprint.claim_id):
                forms = candidate_forms(blueprint)
                self.assertEqual(len(forms), 256)
                self.assertEqual(len(set(forms)), 256)
                self.assertEqual(sum(form == unique_survivor(blueprint) for form in forms), 1)
                rows = candidate_rows(blueprint)
                self.assertEqual(len(rows), 256)
                self.assertEqual(sum(row["candidate_id"] == survivor_id(blueprint) for row in rows), 1)

    def test_dependencies_are_admitted_upstream_or_earlier_medicine(self) -> None:
        admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if row.get("model_admitted") is True}
        earlier: set[str] = set()
        for blueprint in MEDICINE_BLUEPRINTS:
            self.assertFalse(set(blueprint.dependencies) - admitted - earlier)
            earlier.add(blueprint.claim_id)

    def test_sources_bindings_and_failed_transports_are_complete(self) -> None:
        validate_sources(ROOT)
        self.assertEqual(sum(row.transport_status == "captured" for row in MEDICINE_AUTHORITY_SOURCES), 11)
        self.assertEqual(sum(row.transport_status == "failed" for row in MEDICINE_AUTHORITY_SOURCES), 2)
        for spec in MEDICINE_SPECS:
            binding = BINDING_BY_CLAIM[spec.claim_id]
            self.assertGreaterEqual(len(binding.requirements), 2)
            for requirement in binding.requirements:
                self.assertIn(requirement.fragment.casefold(), source_corpus(ROOT, requirement.source_id))

    def test_exact_clinical_table_censuses(self) -> None:
        diagnostic = diagnostic_table_certificate()
        trial = two_arm_outcome_certificate()
        self.assertEqual(diagnostic["cell_count"], 4)
        self.assertIs(diagnostic["complete"], True)
        self.assertEqual(trial["cell_count"], 4)
        self.assertIs(trial["complete"], True)
        self.assertEqual(exact_share(1, 2), (1, 2))
        with self.assertRaises(ValueError):
            exact_share(0, 2)

    def test_no_axiom_parameter_or_target_field_in_blueprints(self) -> None:
        for blueprint in MEDICINE_BLUEPRINTS:
            self.assertFalse({"axioms", "free_parameters", "target_rows", "source_id"} & set(blueprint.__dataclass_fields__))
            self.assertTrue(all(witness[2] for witness in blueprint.operational_witnesses))
        self.assertTrue(validate_pre_source_seal(ROOT).startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()

