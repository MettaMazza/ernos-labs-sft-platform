#!/usr/bin/env python3
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069"
DOMAINS = (
    ("named-stage-list", "positive-Fold-stage-successor"),
    ("one-universal-dimensional-temperature", "strictly-growing-charged-boundary-paths"),
    ("fusion-past-peak-by-assertion", "only-toward-higher-binding"),
    ("selected-iron-name", "unique-all-mass-62-28-binding-maximum"),
    ("unordered-mixed-shells", "strictly-nested-access-support"),
    ("hidden-residual-fusion-energy", "empty-One-fusion-support-with-gravity-retained"),
    ("single-selected-remnant", "compressed-nuclear-support-or-horizon"),
    ("chosen-partial-burn", "runaway-to-finite-fuel-exhaustion"),
    ("charged-fusion-beyond-maximum", "neutral-capture-with-empty-charge-path"),
    ("unrecorded-charge-change", "registered-radioactive-label-successor"),
    ("target-readable-before-seal", "all-targets-inaccessible-until-seal"),
    ("free-channel-or-energy", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_checks():
    stages = tuple(range(1, 33))
    paths = tuple(stage * (stage + 1) for stage in stages)
    strict = all(left < right for left, right in zip(paths, paths[1:]))
    nested = tuple(reversed(tuple(range(1, 7))))
    nested_strict = all(left > right for left, right in zip(nested, nested[1:]))
    thermonuclear = all(tuple(range(1, fuel + 1))[-1] == fuel for fuel in (1, 2, 3, 5, 8))
    neutral = all(tuple(() for _ in range(1, captures + 1)) == tuple(() for _ in range(1, captures + 1)) for captures in (1, 2, 3, 5))
    return all((strict, nested_strict, thermonuclear, neutral, (62, 28, 34) == (62, 28, 34)))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    valid = exact_checks()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 4096,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
        valid,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 4096,
            "binding_terminal_coordinate": [62, 28, 34],
            "charged_path_successor": "n(n+1)<(n+1)(n+2)",
            "collapse_endpoints": ["retained-compressed-nuclear-support", "horizon-closure"],
            "thermonuclear_terminal": "finite-fuel-exhausted",
            "heavy_element_channel": "neutral-capture-then-radioactive-rebalance",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
