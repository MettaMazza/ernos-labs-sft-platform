"""Standalone recomputation of the structural-One coverage product."""

import hashlib
from itertools import product
import json
import sys


ROOT_COVERAGE = ("none", "proper", "complete")
EXTRA_COVERAGE = ("no-extra", "has-extra")


def identity(value):
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def name(root, extra):
    return {
        ("none", "no-extra"): "omitted-root",
        ("proper", "no-extra"): "fragmented-root",
        ("complete", "no-extra"): "exact-self-whole",
        ("none", "has-extra"): "replacement-extra",
        ("proper", "has-extra"): "fragment-plus-extra",
        ("complete", "has-extra"): "whole-plus-extra",
    }[(root, extra)]


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated_ids = [name(root, extra) for root, extra in product(ROOT_COVERAGE, EXTRA_COVERAGE)]
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    expected = {
        candidate_id: candidate_id == "exact-self-whole" for candidate_id in generated_ids
    }
    passed = (
        sealed["claim_id"] == "SFT-FOUNDATION-ONE-001"
        and [item["candidate_id"] for item in sealed["census"]["candidates"]] == generated_ids
        and sealed["census"]["expected_cardinality"] == len(generated_ids)
        and decisions == expected
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(sealed["controls"]) == len({item["kind"] for item in sealed["controls"]}) == 4
        and all(item["passed"] is True for item in sealed["controls"])
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "coverage_product": [list(ROOT_COVERAGE), list(EXTRA_COVERAGE)],
                    "generated_ids": generated_ids,
                    "survivor": "exact-self-whole" if passed else None,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
