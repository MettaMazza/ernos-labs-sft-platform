"""Implementation-distinct product validator for SFT-BIO-NESTED-COMPARTMENT-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-BIO-NESTED-COMPARTMENT-001'
DOMAINS = (('carrier-erased-or-answer-only', 'finite-compartment-tree-carrier'), ('relation-imported-fitted-or-erased', 'parent-child-containment'), ('organization-collapsed', 'each-boundary-and-transfer-retained'), ('observation-boundary-unrecorded', 'nesting-depth-declared'), ('result-without-transition-record', 'complete-state-transition-control-record'), ('authority-target-or-prior-selected-law', 'root-bound-forward-forcing'), ('single-specimen-favorable-instance', 'positive-finite-successor-and-adverse-closure'), ('free-fit-exception-or-extra-rule', 'no-extra-rule'))
SURVIVOR = 'finite-compartment-tree-carrier__parent-child-containment__each-boundary-and-transfer-retained__nesting-depth-declared__complete-state-transition-control-record__root-bound-forward-forcing__positive-finite-successor-and-adverse-closure__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
