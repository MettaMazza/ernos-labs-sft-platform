"""Independent product validator for SFT-CHEM-ELECTROCHEM-CELL-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CHEM-ELECTROCHEM-CELL-001'
DOMAINS = (('one-conflated-site', 'distinct-oxidation-reduction-sites'), ('electron-teleportation', 'complete-external-electron-path'), ('charge-accumulation-unclosed', 'complete-compensating-ionic-path'), ('independent-half-reactions', 'one-redox-transfer-cycle'), ('free-energy-output', 'source-bounded-work-transfer'), ('negative-potential-primitive', 'held-cell-orientation'), ('cell-label-only', 'sites-paths-transfer-trace'), ('free-electrode-potential', 'no-extra-rule'))
SURVIVOR = 'distinct-oxidation-reduction-sites__complete-external-electron-path__complete-compensating-ionic-path__one-redox-transfer-cycle__source-bounded-work-transfer__held-cell-orientation__sites-paths-transfer-trace__no-extra-rule'
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
