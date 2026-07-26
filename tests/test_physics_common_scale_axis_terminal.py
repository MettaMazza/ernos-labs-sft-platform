from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.common_scale_axis_terminal_law_v1 import (
    SPEC,
    common_axis_certificate,
    common_rational_rescaling_ratio,
    internal_square_anchor_levels,
    leading_curve_strictly_descends,
    leading_electroweak_share,
    scale_axis_landmarks,
    scale_spacing,
    terminal_electroweak_chain,
    traversal_count,
)
from sft.physics.common_scale_axis_terminal_validation_v1 import authoritative_record, exact_measurement_analysis
from sft.physics.structural_constants import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class CommonScaleAxisTerminalTests(unittest.TestCase):
    def test_exact_axis(self) -> None:
        certificate = common_axis_certificate()
        self.assertEqual(certificate["supports"], (1, 2, 4, 8, 16, 32, 64, 128))
        self.assertEqual(certificate["spacings"], tuple(Fraction(1, value) for value in certificate["supports"]))
        self.assertTrue(all(traversal_count(level) == certificate["supports"][level - 1] for level in range(1, 9)))
        self.assertTrue(all(scale_spacing(level + 1) * 2 == scale_spacing(level) for level in range(1, 8)))

    def test_weak_curve_and_terminal_transport(self) -> None:
        self.assertEqual(tuple(leading_electroweak_share(level) for level in range(1, 5)), (Fraction(9, 25), Fraction(4, 13), Fraction(9, 34), Fraction(25, 106)))
        self.assertTrue(leading_curve_strictly_descends(16))
        self.assertEqual(internal_square_anchor_levels(20), (2,))
        chain = terminal_electroweak_chain()
        self.assertEqual(chain["complete_support"], 16)
        self.assertEqual(chain["active_level"], 13)
        self.assertEqual(chain["base_share"], Fraction(225, 1009))
        self.assertEqual(chain["terminal_share"], Fraction(1930922298157999, 8642477221479757))

    def test_unit_invariance_and_landmarks(self) -> None:
        self.assertEqual(common_rational_rescaling_ratio(Fraction(7, 5), Fraction(11, 3), Fraction(13, 17)), Fraction(21, 55))
        self.assertEqual(tuple(row["support"] for row in scale_axis_landmarks()), (1, 2, 8, 16, 13, 32, 128, 127))

    def test_complete_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 12288)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 12288)

    def test_complete_postseal_vector(self) -> None:
        analysis = exact_measurement_analysis(authoritative_record(ROOT))
        self.assertTrue(analysis["terminal_inside_on_shell_interval"])
        self.assertTrue(analysis["leading_support_eight_inside_APV_interval"])
        self.assertTrue(analysis["E158_interval_strictly_above_MS_Z"])
        self.assertTrue(analysis["APV_interval_strictly_above_MS_Z"])
        self.assertTrue(analysis["eDIS_interval_overlaps_MS_Z"])
        self.assertTrue(analysis["NuTeV_adverse_interval_above_terminal_on_shell"])
        self.assertTrue(analysis["running_certificate_passed"])
        self.assertTrue(analysis["terminal_electroweak_certificate_passed"])
        self.assertTrue(analysis["proton_Planck_certificate_passed"])

    def test_scope(self) -> None:
        SPEC.validate()
        self.assertTrue(any("measured energy" in item for item in SPEC.exclusions))
        self.assertTrue(any("historical-blindness" in item for item in SPEC.exclusions))


if __name__ == "__main__":
    unittest.main()
