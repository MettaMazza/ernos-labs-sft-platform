"""Foundational Biology target-blind derivation and source-boundary tests."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from sft.biology.derivation import BIOLOGY_BLUEPRINTS, candidate_forms, unique_survivor
from sft.biology.external_bindings import BINDING_BY_CLAIM
from sft.biology.generated_law import BIOLOGY_SPECS, validate_pre_source_seal
from sft.biology.obligations import BIOLOGY_OBLIGATIONS, SUBBRANCH_ORDER
from sft.biology.sources import source_corpus, validate_sources
from sft.biology.structural_counts import exact_codon_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


class BiologyFoundationTests(unittest.TestCase):
    def test_complete_prediction_surface_is_pre_source_sealed(self) -> None:
        path = ROOT / "experiments/sealed_predictions/biology_foundation_complete_pre_source.json"
        seal = json.loads(path.read_text(encoding="utf-8"))
        claimed = seal.pop("sealed_payload_hash")
        self.assertEqual(claimed, "sha256:4b3e1ba191d363a1b67e1a02853f071cdf2c9d3d86081fced05ab3c5d079e639")
        self.assertEqual(sha256_identity(seal), claimed)
        self.assertEqual(seal["required_claim_count"], 75)
        self.assertEqual(seal["candidate_count"], 19_200)
        for path_key, hash_key in (("inventory_path", "inventory_hash"), ("structural_counts_path", "structural_counts_hash"), ("derivation_path", "derivation_hash")):
            self.assertEqual(hash_file(ROOT / seal[path_key]), seal[hash_key])
        self.assertIs(seal["external_source_identities_selected"], False)
        self.assertIs(seal["external_target_content_opened"], False)

    def test_inventory_blueprints_and_specs_are_exactly_aligned(self) -> None:
        identities = tuple(row.claim_id for row in BIOLOGY_OBLIGATIONS)
        self.assertEqual(identities, tuple(row.claim_id for row in BIOLOGY_BLUEPRINTS))
        self.assertEqual(identities, tuple(row.claim_id for row in BIOLOGY_SPECS))
        self.assertEqual(len(identities), 75)
        self.assertEqual(tuple(dict.fromkeys(row.subbranch for row in BIOLOGY_OBLIGATIONS)), SUBBRANCH_ORDER)

    def test_every_blueprint_exhausts_256_forms_with_one_survivor(self) -> None:
        for blueprint in BIOLOGY_BLUEPRINTS:
            with self.subTest(claim_id=blueprint.claim_id):
                forms = candidate_forms(blueprint)
                self.assertEqual(len(forms), 256)
                self.assertEqual(len(set(forms)), 256)
                self.assertEqual(sum(form == unique_survivor(blueprint) for form in forms), 1)
                rows = candidate_rows(blueprint)
                self.assertEqual(len(rows), 256)
                self.assertEqual(sum(row["candidate_id"] == survivor_id(blueprint) for row in rows), 1)

    def test_dependencies_are_admitted_upstream_or_earlier_biology(self) -> None:
        admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if row.get("model_admitted") is True}
        earlier: set[str] = set()
        for blueprint in BIOLOGY_BLUEPRINTS:
            self.assertFalse(set(blueprint.dependencies) - admitted - earlier)
            earlier.add(blueprint.claim_id)

    def test_all_sources_and_claim_specific_fragments_reproduce(self) -> None:
        validate_sources(ROOT)
        for spec in BIOLOGY_SPECS:
            binding = BINDING_BY_CLAIM[spec.claim_id]
            self.assertGreaterEqual(len(binding.requirements), 2)
            for requirement in binding.requirements:
                self.assertIn(requirement.fragment.casefold(), source_corpus(ROOT, requirement.source_id))

    def test_exact_codon_census(self) -> None:
        self.assertEqual(exact_codon_certificate(), {"held_distinctions": 2, "alphabet_count": 4, "word_length": 3, "codon_count": 64, "box_count": 16, "box_widths": (4,), "alphabet_complete": True, "codon_census_complete": True, "partition_complete": True, "each_word_once": True})

    def test_no_axiom_parameter_or_target_field_in_blueprints(self) -> None:
        for blueprint in BIOLOGY_BLUEPRINTS:
            self.assertFalse({"axioms", "free_parameters", "target_rows", "source_id"} & set(blueprint.__dataclass_fields__))
            self.assertTrue(all(witness[2] for witness in blueprint.operational_witnesses))
        self.assertTrue(validate_pre_source_seal(ROOT).startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
