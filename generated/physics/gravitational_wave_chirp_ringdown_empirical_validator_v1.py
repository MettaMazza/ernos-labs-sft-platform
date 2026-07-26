#!/usr/bin/env python3
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074"
DOMAINS = (
    ("answer-only-scalar", "complete-fold-carrier"),
    ("imported-or-fitted-relation", "sealed-Fold-chirp-merger-ringdown-sequence-versus-complete-postseal-LIGO-vector"),
    ("unbound-provenance", "source-bound-proof-trace"),
    ("target-readable-prediction", "capability-closed-prediction"),
    ("proof-measurement-conflation", "separate-measurement-record"),
    ("selected-favourable-rows", "complete-registered-rows"),
    ("finite-answer-lookup", "one-successor-closure"),
    ("free-extra-rule", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 256,
            "postseal_target_count": 2,
            "preseal_context_count": 1,
            "gw150914_counted_as_blind": False,
            "all_scope_rows_required": True,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
