from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.elements_periodicity_batch_1 import ELEMENTS_PERIODICITY_BATCH_1_SPECS
from sft.chemistry.generated_law import BlindExternalChemistryValidator
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryElementsPeriodicityBatchOneTests(unittest.TestCase):
    def test_batch_contains_the_first_four_registered_element_laws(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in ELEMENTS_PERIODICITY_BATCH_1_SPECS),
            (
                "SFT-CHEM-ELEM-ELEMENT-001",
                "SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
                "SFT-CHEM-ELEM-ISOTOPE-001",
                "SFT-CHEM-ELEM-ATOMIC-WEIGHT-001",
            ),
        )

    def test_each_law_exhausts_its_content_specific_product(self) -> None:
        for spec in ELEMENTS_PERIODICITY_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(identity == survivor_id(spec) for identity in identities), 1)

    def test_source_derived_iupac_rows_and_tampered_controls_pass(self) -> None:
        for spec in ELEMENTS_PERIODICITY_BATCH_1_SPECS:
            result = BlindExternalChemistryValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "elements-test-seal")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_preceding_chemistry_batches_remain_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/measurement_identity_batch_2.py": "sha256:39560a34d9ffa3e6504fad03ccbd5e5d9d0cf59f16b4da050d3fe4e2ef2a52a1",
            "experiments/external_sources/chemistry/observations_measurement_identity_batch_2.json": "sha256:0a46cd00db417d71cef397906ce5d9a0703fa50f7d1fcf50d5985cd2ded90266",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
