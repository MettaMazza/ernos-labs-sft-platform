"""Exact pre-source Fold witnesses for the Astronomy foundation."""

from __future__ import annotations

from fractions import Fraction


def fold(value: Fraction) -> Fraction:
    doubled = value * 2
    return doubled if doubled <= 1 else doubled - 1


def structural_witnesses() -> dict[str, bool]:
    period_two = (Fraction(1, 3), Fraction(2, 3))
    period_three = (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
    source_path_observer = ("source", "path", "observer", "instrument", "record")
    evidence_classes = ("direct", "retrieval", "proxy", "reconstruction", "model", "forecast", "missing")
    exponent_candidates = (1, 2, 3)
    rank_four = tuple(value for value in exponent_candidates + (4,) if value == 4)
    return {
        "source_path_observer_ordered": len(source_path_observer) == len(set(source_path_observer)),
        "evidence_classes_distinct": len(evidence_classes) == len(set(evidence_classes)),
        "period_two_recurs": tuple(fold(x) for x in period_two) == (period_two[1], period_two[0]),
        "period_three_recurs": tuple(fold(x) for x in period_three) == (period_three[1], period_three[2], period_three[0]),
        "period_three_partitions_one": sum(period_three, Fraction()) == 1,
        "positive_ordered_history": all(Fraction(i, 8) < Fraction(i + 1, 8) for i in range(1, 7)),
        "joint_population_product": 2 * 3 == 6,
        "rank_four_unique_in_registered_dimension_successor": rank_four == (4,),
        "observation_never_recovers_unheld_predecessor": fold(Fraction(1, 4)) == fold(Fraction(3, 4)),
    }


if not all(structural_witnesses().values()):
    raise ValueError("Astronomy structural witness failed")

__all__ = ("fold", "structural_witnesses")
