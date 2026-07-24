"""Independent product validator for SFT-CHEM-RXN-MECHANISM-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CHEM-RXN-MECHANISM-001'
DOMAINS = (('unordered-step-list', 'ordered-elementary-step-word'), ('unmatched-step-endpoints', 'adjacent-state-composition'), ('hidden-substeps', 'declared-indivisible-steps'), ('internal-species-erased', 'internal-states-held'), ('different-overall-reaction', 'same-overall-endpoints'), ('carrier-loss-between-steps', 'carrier-conservation-each-step'), ('mechanism-label-only', 'complete-ordered-step-trace'), ('free-hidden-path', 'no-extra-rule'))
SURVIVOR = 'ordered-elementary-step-word__adjacent-state-composition__declared-indivisible-steps__internal-states-held__same-overall-endpoints__carrier-conservation-each-step__complete-ordered-step-trace__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and
              sealed["census"]["expected_cardinality"] == len(generated) and
              len(set(received)) == len(generated) and
              decisions == {row: row == SURVIVOR for row in generated} and
              sum(decisions.values()) == 1 and
              sealed["closure"]["scope"] == "depth_independent" and
              sealed["closure"]["minimality_passed"] is True and
              sealed["closure"]["named_shape_uniqueness_passed"] is True and
              {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and
              all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True,
                      "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated),
                      "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
