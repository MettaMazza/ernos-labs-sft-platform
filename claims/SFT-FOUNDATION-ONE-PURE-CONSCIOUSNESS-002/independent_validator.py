"""Standalone regeneration of the One-as-pure-consciousness product."""

import json
from itertools import product
import sys


CLAIM_ID = "SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002"
COVERAGE = ("none", "proper", "complete")
AXES = ("observer", "observed", "content", "succession", "report", "substrate")
STATES = ("undifferentiated", "added")
EXACT_RESULT = (
    "complete-presented-occurrence__observer-undifferentiated__"
    "observed-undifferentiated__content-undifferentiated__"
    "succession-undifferentiated__report-undifferentiated__"
    "substrate-undifferentiated"
)


def records():
    generated = []
    for coverage, states in product(COVERAGE, product(STATES, repeat=len(AXES))):
        coordinates = tuple(zip(AXES, states))
        identifier = "__".join(
            (f"{coverage}-presented-occurrence",)
            + tuple(f"{axis}-{state}" for axis, state in coordinates)
        )
        generated.append((identifier, coverage, coordinates))
    return generated


def expected_survival(coverage, coordinates):
    return coverage == "complete" and all(
        state == "undifferentiated" for _, state in coordinates
    )


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = records()
    generated_ids = [row[0] for row in generated]
    expected = {
        identifier: expected_survival(coverage, coordinates)
        for identifier, coverage, coordinates in generated
    }
    decisions = {
        item["candidate_id"]: item["survives"] for item in sealed["decisions"]
    }
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and sealed["census"]["expected_cardinality"] == 192
        and [item["candidate_id"] for item in sealed["census"]["candidates"]]
        == generated_ids
        and len(generated_ids) == len(set(generated_ids)) == 192
        and decisions == expected
        and [identifier for identifier, survives in expected.items() if survives]
        == [EXACT_RESULT]
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(controls) == len({item["kind"] for item in controls}) == 4
        and all(item["passed"] is True for item in controls)
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "presentation_coverage": list(COVERAGE),
                    "differentiation_axes": list(AXES),
                    "differentiation_states": list(STATES),
                    "generated_count": len(generated_ids),
                    "survivor": EXACT_RESULT if passed else None,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
