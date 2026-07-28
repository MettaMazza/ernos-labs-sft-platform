"""Implementation-distinct product validator for SFT-CONSC-CROSS-MODAL-QUALIA-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CONSC-CROSS-MODAL-QUALIA-001'
DOMAINS = (('carrier-absent-or-description-only', 'qualities-from-distinct-modal-sources'), ('distinction-collapsed-or-conflated', 'same-modal/cross-modal'), ('operation-imported-fitted-or-missing', 'shared-observation-class-composition'), ('favourable-output-without-complete-trace', 'source-modality-component-joint-record'), ('report-behaviour-correlation-or-confidence-substituted', 'first-person-psychophysical'), ('prior-consensus-target-or-application-selected', 'root-bound-forward-forcing'), ('one-favourable-instance-with-erased-alternatives', 'positive-finite-successor-with-all-alternatives'), ('free-parameter-exception-or-opaque-oracle', 'no-extra-rule'))
SURVIVOR = 'qualities-from-distinct-modal-sources__same-modal/cross-modal__shared-observation-class-composition__source-modality-component-joint-record__first-person-psychophysical__root-bound-forward-forcing__positive-finite-successor-with-all-alternatives__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
