"""Versioned KIN-007 late-time observation-class reconstruction.

The primary experiment does not distinguish a unique late atomic structure.
This module therefore preserves and enumerates the exact distinctions the
source *does* report, including the adverse interleaved-dark control.  It never
converts a non-unique observation into a favorable singleton.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/kin-007-sequential-mechanism-v1"
    / "sequential-mechanism-primary-records-v1.json"
)


@dataclass(frozen=True)
class LateObservationClass:
    target_id: str
    elapsed_seconds: Fraction | None
    source_observation: str
    members: tuple[str, ...]
    unique_atomic_structure_selected: bool = False


def reconstruct_late_observation_classes(path: Path = PRIMARY) -> tuple[LateObservationClass, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = {row["source_row"]: row for row in document["complete_source_ordered_target_vector"]}
    expected_rows = (6, 7, 16, 17)
    if any(number not in rows for number in expected_rows):
        raise ValueError("KIN-007 late-time or adverse-control source row changed")

    one_ms = rows[6]
    seventeen_ms = rows[7]
    adverse = rows[16]
    boundary = rows[17]
    if (
        one_ms["assignment_status"] != "unresolved-multiple-intermediate-mixture; no precise single atomic model"
        or seventeen_ms["assignment_status"] != "unresolved-multiple-intermediate-mixture; no precise single atomic model"
        or adverse["source_status"] != "unfavorable control retained without correction or deletion"
        or boundary["source_status"] != "unresolved mechanism boundary retained without inferred intermediate"
    ):
        raise ValueError("KIN-007 source status changed")

    result = (
        LateObservationClass(
            one_ms["target_id"],
            Fraction(one_ms["elapsed_second_exact_fraction"]),
            one_ms["observed_state"],
            (
                "weak-negative-density-toward-COeq2",
                "possible-third-CO-release-within-multiple-intermediate-mixture",
            ),
        ),
        LateObservationClass(
            seventeen_ms["target_id"],
            Fraction(seventeen_ms["elapsed_second_exact_fraction"]),
            seventeen_ms["observed_state"],
            (
                "weak-negative-density-toward-COeq2",
                "possible-third-CO-release",
                "possible-CO-rebinding",
                "multiple-intermediate-mixture",
            ),
        ),
        LateObservationClass(
            adverse["target_id"],
            None,
            adverse["observed_adverse_result"],
            ("possible-light-contamination", "reduced-COax-difference-density"),
        ),
        LateObservationClass(
            boundary["target_id"],
            None,
            boundary["source_disclosure"],
            ("simultaneous-multiple-intermediates", "possible-Mn-rebinding"),
        ),
    )
    if (
        tuple(row.target_id for row in result)
        != (
            "KIN-007-SEQUENTIAL-RECORD-06",
            "KIN-007-SEQUENTIAL-RECORD-07",
            "KIN-007-SEQUENTIAL-RECORD-16",
            "KIN-007-SEQUENTIAL-RECORD-17",
        )
        or any(row.unique_atomic_structure_selected for row in result)
        or result[0].elapsed_seconds != Fraction(1, 1000)
        or result[1].elapsed_seconds != Fraction(17, 1000)
    ):
        raise ValueError("KIN-007 exact observation-class reconstruction changed")
    return result


__all__ = ("LateObservationClass", "PRIMARY", "reconstruct_late_observation_classes")
