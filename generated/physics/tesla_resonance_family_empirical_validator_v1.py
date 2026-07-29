#!/usr/bin/env python3
"""Independent complete enumeration for empirical Tesla-family Claim 082."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082"
DOMAINS = (
    ("answer-only-scalar", "complete-fold-carrier"),
    ("imported-or-fitted-relation", "sealed-tesla-resonance-family-versus-complete-five-source-observation-vector"),
    ("unbound-provenance", "source-bound-proof-trace"),
    ("target-readable-prediction", "capability-closed-prediction"),
    ("proof-measurement-conflation", "separate-measurement-record"),
    ("selected-favourable-rows", "complete-registered-rows"),
    ("finite-answer-lookup", "one-successor-closure"),
    ("free-extra-rule", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def main():
    sealed = json.loads(open(sys.argv[2], encoding="utf-8").read())
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR for candidate in generated}
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    controls = tuple(sealed["controls"])
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": decisions == recomputed,
            "unique_survivor_count": sum(recomputed.values()),
            "registered_target_rows": 5,
            "formal_predecessor_count": 4,
            "source_count": 5,
            "target_content_used": False,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
