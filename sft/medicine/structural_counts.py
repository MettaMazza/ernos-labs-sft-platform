"""Small exact certificates used by the Medicine foundational laws."""

from __future__ import annotations

from itertools import product


def diagnostic_table_certificate() -> dict[str, object]:
    condition = ("condition-held", "condition-absence-held")
    test = ("test-held", "test-absence-held")
    cells = tuple(product(condition, test))
    return {
        "condition_labels": condition,
        "test_labels": test,
        "cells": cells,
        "cell_count": len(cells),
        "complete": len(cells) == 4 and len(set(cells)) == 4,
        "absence_semantics": "held label; never numerical-zero ontology",
    }


def two_arm_outcome_certificate() -> dict[str, object]:
    arms = ("intervention", "comparator")
    outcomes = ("outcome-held", "outcome-absence-held")
    cells = tuple(product(arms, outcomes))
    return {
        "arms": arms,
        "outcomes": outcomes,
        "cells": cells,
        "cell_count": len(cells),
        "complete": len(cells) == 4 and len(set(cells)) == 4,
        "absence_semantics": "held label; never numerical-zero ontology",
    }


def exact_share(part: int, whole: int) -> tuple[int, int]:
    if part < 1 or whole < 1 or part > whole:
        raise ValueError("SFT exact shares require positive finite counts with part no greater than whole")
    return part, whole


__all__ = ("diagnostic_table_certificate", "two_arm_outcome_certificate", "exact_share")

