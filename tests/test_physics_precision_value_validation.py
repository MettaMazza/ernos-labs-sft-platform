"""Focused exact checks for Physics precision source comparisons."""

from pathlib import Path
import unittest

from sft.physics.precision_value_validation_v1 import (
    PDG_LABEL,
    codata_hierarchy_interval,
    electroweak_comparison,
)
from sft.physics.precision_value_laws_v1 import terminal_proton_planck_squared_ratio


ROOT = Path(__file__).resolve().parents[1]


class PrecisionValueValidationTests(unittest.TestCase):
    def test_complete_electroweak_vector(self) -> None:
        record = electroweak_comparison(ROOT)
        self.assertEqual(record["classification"], PDG_LABEL)
        self.assertEqual(
            record["outcomes"],
            {
                "on_shell_weak_share_inside": True,
                "compatible_input_wz_inside": True,
                "all_input_wz_inside": False,
            },
        )

    def test_codata_hierarchy(self) -> None:
        lower, upper = codata_hierarchy_interval(ROOT)
        self.assertLessEqual(lower, terminal_proton_planck_squared_ratio())
        self.assertLessEqual(terminal_proton_planck_squared_ratio(), upper)


if __name__ == "__main__":
    unittest.main()
