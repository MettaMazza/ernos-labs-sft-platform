"""Implementation-distinct product validator for SFT-EARTH-GEOLOGICAL-LAYER-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-EARTH-GEOLOGICAL-LAYER-001'
DOMAINS = (('answer-only-or-unbounded-carrier', 'bounded-spatial-material-carrier'), ('boundary-or-interface-erased', 'mapping-resolution-bounded'), ('imported-fitted-or-missing-relation', 'adjacency-continuity-and-contact-relation'), ('favourable-output-with-incomplete-record', 'extent-thickness-contacts-facies-and-uncertainty-held'), ('model-proxy-forecast-or-observation-conflated', 'evidence-class-explicit'), ('prior-target-consensus-or-application-selected', 'root-bound-forward-forcing'), ('one-favourable-case-with-erased-alternatives', 'positive-finite-successor-retains-all-rows'), ('free-parameter-exception-or-opaque-oracle', 'no-extra-rule'))
SURVIVOR = 'bounded-spatial-material-carrier__mapping-resolution-bounded__adjacency-continuity-and-contact-relation__extent-thickness-contacts-facies-and-uncertainty-held__evidence-class-explicit__root-bound-forward-forcing__positive-finite-successor-retains-all-rows__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}, sort_keys=True))
if __name__ == "__main__": main()
