from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.bonding_molecular_batch_1 import (
    BONDING_MOLECULAR_BATCH_1_SPECS,
    BondSupport,
    connected_collective_support,
    joining_multiplicity,
)
from sft.chemistry.generated_goldbook_extended_law import (
    BlindExtendedGoldBookValidator,
    source_derived_extended_targets,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryBondingMolecularBatchOneTests(unittest.TestCase):
    def test_batch_closes_the_first_six_bonding_obligations(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in BONDING_MOLECULAR_BATCH_1_SPECS),
            (
                "SFT-CHEM-BOND-CHEMICAL-BOND-001",
                "SFT-CHEM-BOND-COVALENT-001",
                "SFT-CHEM-BOND-IONIC-001",
                "SFT-CHEM-BOND-METALLIC-001",
                "SFT-CHEM-BOND-ORDER-001",
                "SFT-CHEM-BOND-LENGTH-STRENGTH-001",
            ),
        )

    def test_each_content_grammar_is_complete_and_has_one_survivor(self) -> None:
        for spec in BONDING_MOLECULAR_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(row == survivor_id(spec) for row in identities), 1)

    def test_bond_support_distinguishes_occurrences_not_element_labels(self) -> None:
        same_element_bond = BondSupport(
            "hydrogen-occurrence-one",
            "hydrogen-occurrence-two",
            (HeldLabel("joining", "shared-support"),),
            True,
        )
        self.assertEqual(joining_multiplicity(same_element_bond), PositiveCount(1))
        with self.assertRaises(InadmissibleExactValue):
            BondSupport(
                "same-atomic-occurrence",
                "same-atomic-occurrence",
                (HeldLabel("joining", "shared-support"),),
                True,
            )

    def test_metallic_support_requires_complete_connected_network(self) -> None:
        self.assertTrue(
            connected_collective_support(
                ("cell-A", "cell-B", "cell-C"),
                (("cell-A", "cell-B"), ("cell-B", "cell-C")),
            )
        )
        self.assertFalse(
            connected_collective_support(
                ("cell-A", "cell-B", "cell-C"),
                (("cell-A", "cell-B"),),
            )
        )

    def test_definition_and_notes_are_opened_only_by_post_seal_validator(self) -> None:
        for spec in BONDING_MOLECULAR_BATCH_1_SPECS:
            rows, registry_hash = source_derived_extended_targets(ROOT, spec)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["observed_label"], spec.expected_observation_label)
            self.assertTrue(registry_hash.startswith("sha256:"))
            result = BlindExtendedGoldBookValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "bonding-test-seal")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_observation_registry_contains_extractions_not_target_labels(self) -> None:
        registry = json.loads(
            (
                ROOT
                / "experiments/external_sources/chemistry/observations_bonding_molecular_batch_1.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            registry["schema"],
            "sft-v3-chemistry-extended-source-derived-observations/1",
        )
        for row in registry["observations"]:
            self.assertNotIn("observed_label", row)
            self.assertNotIn("expected_observation_label", row)

    def test_registered_iupac_snapshots_are_byte_exact(self) -> None:
        expected = {
            "CT07009": "sha256:691e8522684b2e4290c207ae988a4689d1ab255cdd5fca4ed66a1bd557fa4207",
            "C01384": "sha256:5106a40f5b1c372a570fc42f3cb1641b63a270454e4a7138699c584754294622",
            "IT07058": "sha256:85d726bab39480e944dfd95e31889931459f4436480d751d73df058c68ad232e",
            "08789": "sha256:570755940f01bfa32741b03b6b2f22b02742101605a2263e57369966ea433abd",
            "B00707": "sha256:f8056279c1ae14cc144d184f01797de9aa2d8fb69ed868b9753ba2e63255dccf",
            "B00702": "sha256:f53dadb6357406a52d41d9d4be1f7698d4db3b8954b04f798ba823b18c40c821",
        }
        self.assertEqual(
            {
                code: hash_file(
                    ROOT
                    / f"experiments/external_sources/chemistry/snapshots/goldbook-terms/{code}.json"
                )
                for code in expected
            },
            expected,
        )

    def test_all_preceding_chemistry_authorities_remain_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/generated_law.py": "sha256:678de1061dcd4b4a24deefd7757045729d89677d6170bd907cde70bc9ca2e15a",
            "sft/chemistry/catalog.py": "sha256:90750420738638bdadd783f0fb83bc667ee414cc48036e5cdc2f9a2a61089fd6",
            "sft/chemistry/obligations.py": "sha256:b502afe57640149166b4ca69b433d02b3361155eb624f9af8cb8918f77ac0ad7",
            "sft/chemistry/measurement_identity_batch_2.py": "sha256:39560a34d9ffa3e6504fad03ccbd5e5d9d0cf59f16b4da050d3fe4e2ef2a52a1",
            "sft/chemistry/elements_periodicity_batch_1.py": "sha256:a311a161899600a5b2a6bc7eaf48db552ca7cd29452578fe888ba13a69c420d1",
            "sft/chemistry/elements_periodicity_batch_2.py": "sha256:0db053985b28ab518b6b7cae11e03904b9409c29aee9e4a179e547a2669c3b4f",
        "sft/chemistry/generated_periodic_law.py": "sha256:3681af2f6f16947a6f0a58bdebcc161a7c11b2f096269d550a9e97e9a3b69926",
            "sft/chemistry/composition_stoichiometry_batch_1.py": "sha256:d4829957d2f8b7b00f51037649cad06cb26acbca17e2a48774ec0097aa66438b",
            "experiments/external_sources/chemistry/observations_composition_stoichiometry_batch_1.json": "sha256:9cc1cc0830eca089aab602a249d8c8b9e0368551b83c3392d971161548260af7",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
