from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.elements_periodicity_batch_2 import ELEMENTS_PERIODICITY_BATCH_2_SPECS
from sft.chemistry.generated_periodic_law import (
    BlindPeriodicChemistryValidator,
    periodic_pdf_text,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


class ChemistryElementsPeriodicityBatchTwoTests(unittest.TestCase):
    def test_batch_contains_all_six_remaining_element_laws(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in ELEMENTS_PERIODICITY_BATCH_2_SPECS),
            (
                "SFT-CHEM-ELEM-PERIODIC-ORDER-001",
                "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001",
                "SFT-CHEM-ELEM-GROUP-PERIOD-001",
                "SFT-CHEM-ELEM-VALENCE-001",
                "SFT-CHEM-ELEM-ION-001",
                "SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001",
            ),
        )

    def test_each_law_exhausts_one_content_specific_product(self) -> None:
        for spec in ELEMENTS_PERIODICITY_BATCH_2_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(identity == survivor_id(spec) for identity in identities), 1)

    def test_mixed_source_rows_and_tampered_controls_pass(self) -> None:
        for spec in ELEMENTS_PERIODICITY_BATCH_2_SPECS:
            result = BlindPeriodicChemistryValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "periodic-test-seal")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_pdf_parser_reconstructs_source_text_without_pdf_dependency(self) -> None:
        raw, joined_digits = periodic_pdf_text(
            ROOT
            / "experiments/external_sources/chemistry/snapshots/iupac-periodic-table-04may22.pdf"
        )
        self.assertIn("atomic number", raw)
        self.assertIn("1 H hydrogen", raw)
        self.assertIn("118 Og oganesson", joined_digits)
        self.assertIn("This version is dated 4 May 2022", raw)

    def test_registry_contains_no_prediction_labels_before_custody_resolution(self) -> None:
        path = (
            ROOT
            / "experiments/external_sources/chemistry/observations_elements_periodicity_batch_2.json"
        )
        registry = json.loads(path.read_text(encoding="utf-8"))
        for observation in registry["observations"]:
            self.assertNotIn("observed_label", observation)
            self.assertNotIn("expected_observation_label", observation)

    def test_all_preceding_chemistry_authorities_remain_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/generated_law.py": "sha256:678de1061dcd4b4a24deefd7757045729d89677d6170bd907cde70bc9ca2e15a",
            "sft/chemistry/catalog.py": "sha256:90750420738638bdadd783f0fb83bc667ee414cc48036e5cdc2f9a2a61089fd6",
            "sft/chemistry/obligations.py": "sha256:b502afe57640149166b4ca69b433d02b3361155eb624f9af8cb8918f77ac0ad7",
            "experiments/external_sources/chemistry/observations.json": "sha256:3cc52c9bc35d2625b26940a92b9f5f26b1a75f58e8f7493b224e033c94464c62",
            "sft/chemistry/measurement_identity_batch_2.py": "sha256:39560a34d9ffa3e6504fad03ccbd5e5d9d0cf59f16b4da050d3fe4e2ef2a52a1",
            "experiments/external_sources/chemistry/observations_measurement_identity_batch_2.json": "sha256:0a46cd00db417d71cef397906ce5d9a0703fa50f7d1fcf50d5985cd2ded90266",
            "sft/chemistry/elements_periodicity_batch_1.py": "sha256:a311a161899600a5b2a6bc7eaf48db552ca7cd29452578fe888ba13a69c420d1",
            "experiments/external_sources/chemistry/observations_elements_periodicity_batch_1.json": "sha256:3b5f2d9bba72ab27bd2b6684815e8d9bedfdbad447ed12c76c4fc299a2eb276a",
            "sft/chemistry/elements_periodicity_batch_2.py": "sha256:0db053985b28ab518b6b7cae11e03904b9409c29aee9e4a179e547a2669c3b4f",
        "sft/chemistry/generated_periodic_law.py": "sha256:3681af2f6f16947a6f0a58bdebcc161a7c11b2f096269d550a9e97e9a3b69926",
            "experiments/external_sources/chemistry/observations_elements_periodicity_batch_2.json": "sha256:f67e0026a0320f47e52855f8dced9038a1148cfa5cd91763d7aa276b16313be5",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
