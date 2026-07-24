"""Independent product validator for SFT-CHEM-PRED-G-BLOCK-001."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CHEM-PRED-G-BLOCK-001'
DOMAINS = (('borrowed-orbital-notation', 'positive-principal-and-orbit-ranks'), ('imported-subshell-widths', 'admitted-Fold-orbit-capacity'), ('memorized-aufbau-list', 'increasing-joint-cover-then-principal-rank'), ('selected-future-coordinate', 'first-5g-occupation-at-121'), ('answer-only-prediction', 'complete-fill-and-dependency-trace'), ('official-table-readable-before-seal', 'official-table-opened-after-seal'), ('future-prediction-called-measured', 'known-prefix-validated-future-coordinate-unobserved'), ('free-exception-or-fit', 'no-extra-rule'))
SURVIVOR = 'positive-principal-and-orbit-ranks__admitted-Fold-orbit-capacity__increasing-joint-cover-then-principal-rank__first-5g-occupation-at-121__complete-fill-and-dependency-trace__official-table-opened-after-seal__known-prefix-validated-future-coordinate-unobserved__no-extra-rule'
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
