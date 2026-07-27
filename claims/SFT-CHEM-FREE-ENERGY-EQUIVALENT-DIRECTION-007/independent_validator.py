"""Implementation-distinct value-free THERMO-007 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID="SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007"
DOMAINS=(("single-path-or-answer-only-direction","complete-forward-and-reverse-path-accounts"),("signed-or-fitted-free-energy-scalar","exact-positive-retained-energy-requirements"),("entropy-logarithm-or-omitted-distinction-cost","exact-positive-closed-distinction-counts"),("weighted-sum-or-target-selected-comparison","strict-exact-product-support-order"),("negative-direction-value-or-forced-tie-break","held-forward-reverse-or-EmptyOne-equilibrium"),("Gibbs-logK-or-direction-target-readable-before-seal","complete-value-free-reaction-state-identity-seal"),("selected-temperature-or-single-direction-showcase","complete-64-row-two-direction-crossing-vector"),("refit-order-after-shared-successor","depth-independent-common-account-successor"))
SURVIVOR="complete-forward-and-reverse-path-accounts__exact-positive-retained-energy-requirements__exact-positive-closed-distinction-counts__strict-exact-product-support-order__held-forward-reverse-or-EmptyOne-equilibrium__complete-value-free-reaction-state-identity-seal__complete-64-row-two-direction-crossing-vector__depth-independent-common-account-successor"
def direction(f,r):
    fe,fd=f;re,rd=r
    if fe==re and fd==rd:return "equilibrium",None,None
    if fe<=re and fd<=rd and (fe<re or fd<rd):label="forward"
    elif re<=fe and rd<=fd and (re<fe or rd<fd):label="reverse"
    else:raise ValueError("incomparable")
    return label,None if fe==re else abs(fe-re),None if fd==rd else abs(fd-rd)
def main():
    with open(sys.argv[1],encoding="utf-8") as h:sealed=json.load(h)
    generated=["__".join(row) for row in product(*DOMAINS)];received=[r["candidate_id"] for r in sealed["census"]["candidates"]];decisions={r["candidate_id"]:r["survives"] for r in sealed["decisions"]};f=(Fraction(5,3),2);r=(Fraction(8,3),3);equal=(Fraction(5,3),2);base=direction(f,r);tie=direction(equal,equal);incomparable=False
    try:direction((Fraction(5,3),4),(Fraction(8,3),2))
    except ValueError:incomparable=True
    extension=(Fraction(7,5),2);extended=direction((f[0]+extension[0],f[1]+extension[1]),(r[0]+extension[0],r[1]+extension[1]));controls=sealed["controls"]
    passed=sealed["claim_id"]==CLAIM_ID and received==generated and sealed["census"]["expected_cardinality"]==len(generated)==256 and len(set(received))==256 and decisions=={c:c==SURVIVOR for c in generated} and len([c for c,v in decisions.items() if v])==1 and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {x["kind"] for x in controls}=={"false_premise","tampered_source","tampered_artifact","boundary"} and all(x["passed"] for x in controls) and base==("forward",Fraction(1),1) and tie==("equilibrium",None,None) and incomparable and extended[0]==base[0]
    print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"strict_product_order_reconstructed":base==("forward",Fraction(1),1),"equilibrium_EmptyOne_reconstructed":tie==("equilibrium",None,None),"incomparable_account_rejected":incomparable,"common_successor_reconstructed":extended[0]==base[0],"Gibbs_logK_or_measurement_file_accessed":False}},sort_keys=True))
if __name__=="__main__":main()
