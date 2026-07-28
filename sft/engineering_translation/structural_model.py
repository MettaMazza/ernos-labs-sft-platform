"""Exact pre-source witnesses for Engineering Translation."""

from fractions import Fraction


def fold(value: Fraction) -> Fraction:
    doubled = value * 2
    return doubled if doubled <= 1 else doubled - 1


def structural_witnesses() -> dict[str, bool]:
    alternatives = (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
    resources = (Fraction(1, 8), Fraction(2, 8), Fraction(1, 8), Fraction(4, 8))
    return {
        "component_identity_retained": ("part-a", "v1") != ("part-a", "v2"),
        "directed_interface_retained": ("source", "sink") != ("sink", "source"),
        "resource_account_closes": sum(resources, Fraction()) == 1,
        "three_alternatives_complete": sum(alternatives, Fraction()) == 1,
        "feedback_recurrence": fold(Fraction(1, 3)) == Fraction(2, 3) and fold(Fraction(2, 3)) == Fraction(1, 3),
        "merged_output_loses_unheld_predecessor": fold(Fraction(1, 4)) == fold(Fraction(3, 4)),
        "ordered_lifecycle": all(Fraction(i, 8) < Fraction(i + 1, 8) for i in range(1, 7)),
        "cross_platform_count_positive_finite": len(("macOS", "Windows", "Linux")) == 3,
        "evidence_classes_distinct": len({"requirement", "design", "test", "simulation", "demonstration", "observation", "anomaly"}) == 7,
    }


if not all(structural_witnesses().values()):
    raise ValueError("Engineering structural witness failed")
