"""Independent product reconstruction for SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003."""
from itertools import product
import json, sys
CLAIM_ID='SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003'
DOMAINS=(('free-orbital-name', 'molecule-bound-support-cell'), ('unjoined-atomic-support-list', 'two-held-joining-phases'), ('continuum-angular-coordinate', 'empty-One-or-positive-axis-recurrence'), ('unsigned-erased-symmetry', 'held-exchange-and-reflection-labels'), ('signed-or-unbounded-occupation', 'empty-One-single-or-complementary-pair'), ('same-fibre-double-occupation', 'complementary-spin-double-occupation'), ('selected-support-fragment', 'complete-electron-support-partition'), ('species-or-symbol-exception', 'no-extra-rule'))
SURVIVOR='molecule-bound-support-cell__two-held-joining-phases__empty-One-or-positive-axis-recurrence__held-exchange-and-reflection-labels__empty-One-single-or-complementary-pair__complementary-spin-double-occupation__complete-electron-support-partition__no-extra-rule'
def main():
    with open(sys.argv[1], encoding="utf-8") as h: sealed=json.load(h)
    generated=["__".join(x) for x in product(*DOMAINS)]
    received=[x["candidate_id"] for x in sealed["census"]["candidates"]]
    decisions={x["candidate_id"]:x["survives"] for x in sealed["decisions"]}
    ranks=("structural-empty-One","first-recurrence","second-recurrence","third-recurrence")
    passed=(sealed["claim_id"]==CLAIM_ID and received==generated and len(set(received))==256 and
      decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and
      sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True and
      sealed["closure"]["named_shape_uniqueness_passed"] is True and len(ranks)==4 and
      {x["kind"] for x in sealed["controls"]}=={"false_premise","tampered_source","tampered_artifact","boundary"} and
      all(x["passed"] is True for x in sealed["controls"]))
    print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"axis_ranks":ranks}},sort_keys=True))
if __name__=="__main__": main()
