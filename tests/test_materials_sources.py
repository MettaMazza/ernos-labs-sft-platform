"""Post-seal authoritative Materials source custody tests."""

from __future__ import annotations

from pathlib import Path
import unittest

from sft.materials.sources import MATERIALS_AUTHORITY_SOURCES, SOURCE_BY_ID, validate_sources


ROOT = Path(__file__).resolve().parent.parent


class MaterialsSourcesTests(unittest.TestCase):
    def test_all_registered_sources_are_unique_and_byte_sealed(self) -> None:
        validate_sources(ROOT)
        self.assertEqual(len(MATERIALS_AUTHORITY_SOURCES), 33)
        self.assertEqual(len(SOURCE_BY_ID), 33)

    def test_only_measurement_bodies_are_registered(self) -> None:
        self.assertEqual(
            {row.body for row in MATERIALS_AUTHORITY_SOURCES},
            {
                "National Institute of Standards and Technology",
                "Joint Committee for Guides in Metrology / Bureau International des Poids et Mesures",
            },
        )


if __name__ == "__main__":
    unittest.main()
