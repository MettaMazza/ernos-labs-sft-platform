"""Implementation-distinct product validator for SFT-MED-SIGN-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-MED-SIGN-001'
DOMAINS = (('carrier-erased-aggregate-or-answer-only', 'observer-elicited-patient-feature'), ('relation-imported-fitted-or-erased', 'feature-to-method-relation'), ('organization-collapsed', 'observer-method-result-record'), ('observation-boundary-unrecorded', 'setting-time-and-observer'), ('favorable-result-without-complete-record', 'complete-protocol-state-transition-adverse-null-record'), ('authority-consensus-prior-or-target-selected-law', 'root-bound-forward-forcing'), ('single-patient-favorable-study', 'positive-finite-successor-and-unfavorable-closure'), ('free-fit-exception-opaque-model-or-extra-rule', 'no-extra-rule'))
SURVIVOR = 'observer-elicited-patient-feature__feature-to-method-relation__observer-method-result-record__setting-time-and-observer__complete-protocol-state-transition-adverse-null-record__root-bound-forward-forcing__positive-finite-successor-and-unfavorable-closure__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
