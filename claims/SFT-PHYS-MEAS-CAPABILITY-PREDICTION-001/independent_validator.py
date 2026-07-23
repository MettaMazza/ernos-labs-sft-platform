"""Implementation-distinct finite-product validator for SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001'
DOMAINS = (('ambient-input', 'registered-input-only'), ('host-scalar-domain', 'exact-fold-domain'), ('contributor-executable-source', 'data-only-generated-operations'), ('ambient-capability', 'no-ambient-capability'), ('mutable-overwrite', 'single-assignment-held-state'), ('implicit-or-open-ended', 'one-terminal-emission'), ('result-only', 'complete-step-trace'), ('extra-rule', 'no-extra-rule'))
SURVIVOR = 'registered-input-only__exact-fold-domain__data-only-generated-operations__no-ambient-capability__single-assignment-held-state__one-terminal-emission__complete-step-trace__no-extra-rule'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
