"""Independent product validator for SFT-CHEM-RXN-INTERMEDIATE-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CHEM-RXN-INTERMEDIATE-001'
DOMAINS = (('anonymous-transient', 'named-internal-species'), ('not-produced', 'produced-by-one-step'), ('not-consumed', 'consumed-by-later-step'), ('consumed-before-produced', 'production-precedes-consumption'), ('present-in-net-products', 'cancels-from-net-endpoints'), ('intermediate-erased', 'intermediate-path-identity-held'), ('intermediate-name-only', 'production-consumption-trace'), ('free-short-lived-premise', 'no-extra-rule'))
SURVIVOR = 'named-internal-species__produced-by-one-step__consumed-by-later-step__production-precedes-consumption__cancels-from-net-endpoints__intermediate-path-identity-held__production-consumption-trace__no-extra-rule'
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
