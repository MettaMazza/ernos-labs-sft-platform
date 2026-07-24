"""Coverage and exact-fragment checks for Materials external validation."""

from __future__ import annotations

from pathlib import Path
import unittest

from sft.materials.external_bindings import MATERIALS_EXTERNAL_BINDINGS, validate_bindings
from sft.materials.obligations import MATERIALS_OBLIGATIONS


ROOT = Path(__file__).resolve().parent.parent


class MaterialsExternalBindingTests(unittest.TestCase):
    def test_every_claim_has_claim_specific_measurement_body_discriminators(self) -> None:
        validate_bindings(ROOT)
        self.assertEqual(len(MATERIALS_EXTERNAL_BINDINGS), 84)
        self.assertEqual(
            tuple(row.claim_id for row in MATERIALS_EXTERNAL_BINDINGS),
            tuple(row.claim_id for row in MATERIALS_OBLIGATIONS),
        )


if __name__ == "__main__":
    unittest.main()
