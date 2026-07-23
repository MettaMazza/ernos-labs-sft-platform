"""Standalone regeneration of the positive-count representation grammar."""

import hashlib
from itertools import product
import json
import sys


COVERAGE = ("none", "proper", "complete")
MULTIPLICITY = ("once", "duplicated")
EXTRA = ("no-extra", "has-extra")


def identity(value):
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def names():
    result = []
    for coverage in COVERAGE:
        multiplicities = ("not-applicable",) if coverage == "none" else MULTIPLICITY
        for multiplicity, extra in product(multiplicities, EXTRA):
            result.append(f"{coverage}-coverage__{multiplicity}__{extra}")
    return result


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = names()
    expected = {
        candidate_id: candidate_id == "complete-coverage__once__no-extra"
        for candidate_id in generated
    }
    observed = {
        item["candidate_id"]: item["survives"] for item in sealed["decisions"]
    }
    passed = (
        sealed["claim_id"] == "SFT-FOUNDATION-COUNT-001"
        and [item["candidate_id"] for item in sealed["census"]["candidates"]]
        == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and observed == expected
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(sealed["controls"])
        == len({item["kind"] for item in sealed["controls"]})
        == 4
        and all(item["passed"] is True for item in sealed["controls"])
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "coverage": list(COVERAGE),
                    "multiplicity": list(MULTIPLICITY),
                    "extra": list(EXTRA),
                    "generated_ids": generated,
                    "survivor": (
                        "complete-coverage__once__no-extra" if passed else None
                    ),
                    "certificate_identity": identity(
                        {"generated_ids": generated, "decisions": expected}
                    ),
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
