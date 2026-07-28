from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.generated_goldbook_extended_law import BlindExtendedGoldBookValidator
from sft.chemistry.molecular_structure_batch_2 import (
    MOLECULAR_STRUCTURE_BATCH_2_SPECS,
    validate_pre_source_seal,
)
from sft.chemistry.molecular_structure_derivation import (
    GeometryRelation,
    MolecularCarrier,
    complete_geometry,
    molecular_isomers,
    structurally_equivalent,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryMolecularStructureBatchTwoTests(unittest.TestCase):
    def test_batch_closes_the_remaining_six_molecular_obligations(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in MOLECULAR_STRUCTURE_BATCH_2_SPECS),
            (
                "SFT-CHEM-MOL-MOLECULE-001",
                "SFT-CHEM-MOL-GEOMETRY-001",
                "SFT-CHEM-MOL-ISOMER-001",
                "SFT-CHEM-MOL-INTERMOLECULAR-001",
                "SFT-CHEM-MOL-SUPRAMOLECULAR-001",
                "SFT-CHEM-MOL-NETWORK-001",
            ),
        )

    def test_pre_source_seal_binds_all_target_blind_predictions(self) -> None:
        validate_pre_source_seal()
        self.assertEqual(
            hash_file(ROOT / "sft/chemistry/molecular_structure_derivation.py"),
            "sha256:39dab1fec6c9e889b12c65751b46a41b382d8686aaa24569f88d4b98a550c0e5",
        )

    def test_each_content_grammar_exhausts_256_forms_and_one_survivor(self) -> None:
        for spec in MOLECULAR_STRUCTURE_BATCH_2_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(row == survivor_id(spec) for row in identities), 1)

    def test_geometry_requires_every_atomic_pair_once(self) -> None:
        molecule = MolecularCarrier(
            ("centre", "left", "right"),
            ("E", "H", "H"),
            (("centre", "left"), ("centre", "right")),
        )
        complete = (
            GeometryRelation("centre", "left", HeldLabel("orientation", "ray-one")),
            GeometryRelation("centre", "right", HeldLabel("orientation", "ray-two")),
            GeometryRelation("left", "right", HeldLabel("orientation", "separation")),
        )
        self.assertTrue(complete_geometry(molecule, complete))
        self.assertFalse(complete_geometry(molecule, complete[:-1]))

    def test_isomer_check_exhausts_identity_preserving_relabellings(self) -> None:
        chain = MolecularCarrier(
            ("a", "b", "c", "d"),
            ("E", "E", "E", "E"),
            (("a", "b"), ("b", "c"), ("c", "d")),
        )
        relabelled_chain = MolecularCarrier(
            ("w", "x", "y", "z"),
            ("E", "E", "E", "E"),
            (("w", "x"), ("x", "y"), ("y", "z")),
        )
        branch = MolecularCarrier(
            ("i", "j", "k", "l"),
            ("E", "E", "E", "E"),
            (("i", "j"), ("i", "k"), ("i", "l")),
        )
        self.assertTrue(structurally_equivalent(chain, relabelled_chain))
        self.assertTrue(molecular_isomers(chain, branch))

    def test_all_post_seal_official_rows_and_tampered_controls_pass(self) -> None:
        for spec in MOLECULAR_STRUCTURE_BATCH_2_SPECS:
            result = BlindExtendedGoldBookValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "molecular-test-seal")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_preceding_bonding_authorities_are_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/generated_law.py": "sha256:678de1061dcd4b4a24deefd7757045729d89677d6170bd907cde70bc9ca2e15a",
            "sft/chemistry/catalog.py": "sha256:90750420738638bdadd783f0fb83bc667ee414cc48036e5cdc2f9a2a61089fd6",
            "sft/chemistry/obligations.py": "sha256:b502afe57640149166b4ca69b433d02b3361155eb624f9af8cb8918f77ac0ad7",
            "sft/chemistry/composition_stoichiometry_batch_1.py": "sha256:d4829957d2f8b7b00f51037649cad06cb26acbca17e2a48774ec0097aa66438b",
        "sft/chemistry/generated_goldbook_extended_law.py": "sha256:328e90af0dbe88372e8cceea84d1ff16e54b0f128e694e65dbaf4b4252e3fbd5",
            "sft/chemistry/bonding_molecular_batch_1.py": "sha256:7ecd8bbb47755910f21dff24a488509d1d803b1a0446b33d8bb88378fb9280c0",
            "experiments/external_sources/chemistry/observations_bonding_molecular_batch_1.json": "sha256:6abbd6fb6e2725adc2f6a9e3eace92bbbd368d0de38b14b6fe31e91d8f69cd04",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
