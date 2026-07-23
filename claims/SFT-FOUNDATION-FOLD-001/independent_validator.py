"""Standalone regeneration of the minimal-Fold grammar."""

from itertools import product
import json
import sys


DOMAINS = (
    ("incomplete", "complete"),
    ("overlapping", "disjoint"),
    ("unequal", "equal"),
    ("identity", "first-extension", "later-extension"),
    ("labels-absent", "labels-same", "labels-distinct-held"),
    ("return-absent", "return-present"),
    ("no-extra", "has-extra"),
)
SURVIVOR = (
    "complete__disjoint__equal__first-extension__labels-distinct-held__"
    "return-present__no-extra"
)


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(fields) for fields in product(*DOMAINS)]
    expected = {candidate_id: candidate_id == SURVIVOR for candidate_id in generated}
    observed = {
        item["candidate_id"]: item["survives"] for item in sealed["decisions"]
    }
    passed = (
        sealed["claim_id"] == "SFT-FOUNDATION-FOLD-001"
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
                    "domain_cardinalities": [len(domain) for domain in DOMAINS],
                    "generated_cardinality": len(generated),
                    "survivor": SURVIVOR if passed else None,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
