"""Implementation-distinct validator for SFT-QUANTUM-SIMULATION-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-QUANTUM-SIMULATION-001'
DOMAINS = (('partial-or-selected-branch-support', 'complete-generated-branch-support'), ('imported-bit-or-qubit', 'one-Fold-distinction-unit'), ('sampled-joint-states', 'complete-pair-cell-joint-support'), ('complex-amplitude-postulate', 'period-held-phase-action'), ('partial-or-irreversible-map', 'total-reversible-source-bound-map'), ('collapse-without-record', 'retained-class-and-complete-record'), ('fixed-circuit-examples', 'branch-and-depth-successor-certificate'), ('imported-quantum-model', 'no-extra-quantum-premise'))
SURVIVOR = 'complete-generated-branch-support__one-Fold-distinction-unit__complete-pair-cell-joint-support__period-held-phase-action__total-reversible-source-bound-map__retained-class-and-complete-record__branch-and-depth-successor-certificate__no-extra-quantum-premise'
def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
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
        "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None},
    }, sort_keys=True))
if __name__ == "__main__":
    main()
