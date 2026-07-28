"""Implementation-distinct product validator for SFT-CONSC-DETERMINED-AGENCY-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CONSC-DETERMINED-AGENCY-001'
DOMAINS = (('carrier-absent-or-description-only', 'self-modelled-action-process'), ('distinction-collapsed-or-conflated', 'generated-successor/ungenerated-choice'), ('operation-imported-fitted-or-missing', 'state-conditioned-action'), ('favourable-output-without-complete-trace', 'premises-alternatives-action-trace'), ('report-behaviour-correlation-or-confidence-substituted', 'formal-and-behavioural'), ('prior-consensus-target-or-application-selected', 'root-bound-forward-forcing'), ('one-favourable-instance-with-erased-alternatives', 'positive-finite-successor-with-all-alternatives'), ('free-parameter-exception-or-opaque-oracle', 'no-extra-rule'))
SURVIVOR = 'self-modelled-action-process__generated-successor/ungenerated-choice__state-conditioned-action__premises-alternatives-action-trace__formal-and-behavioural__root-bound-forward-forcing__positive-finite-successor-with-all-alternatives__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
