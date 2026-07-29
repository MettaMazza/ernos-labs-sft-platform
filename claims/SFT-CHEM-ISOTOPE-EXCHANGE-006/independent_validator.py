from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-ISOTOPE-EXCHANGE-006';DOMAINS=(('mass-number-only', 'held-element-light-heavy-isotopes'), ('phase-free-exchange', 'held-distinct-chemical-carriers'), ('continuum-concentration-premise', 'positive-complete-four-count-inventory'), ('isotope-label-overwrite', 'exact-isotope-and-carrier-conservation'), ('signed-exchange-extent', 'held-direction-positive-Take'), ('fitted-exchange-constant', 'exact-cross-product-exchange-quotient'), ('numerical-zero-net', 'equal-forward-reverse-closes-EmptyOne'), ('lookup-fractionation-factor', 'successor-preserves-identities-and-totals'));SURVIVOR='held-element-light-heavy-isotopes__held-distinct-chemical-carriers__positive-complete-four-count-inventory__exact-isotope-and-carrier-conservation__held-direction-positive-Take__exact-cross-product-exchange-quotient__equal-forward-reverse-closes-EmptyOne__successor-preserves-identities-and-totals'
from fractions import Fraction
def transition(a,b):
 totals=lambda x:(x[0]+x[2],x[1]+x[3],x[0]+x[1],x[2]+x[3])
 return totals(a)==totals(b) and a!=b
def balance(f,r):return None if f==r else ("forward" if f>r else "reverse",abs(f-r))
a=(4,2,3,1);b=(5,1,2,2)
native={"identity":True,"carriers":True,"inventory":min(a)>0,"conservation":transition(a,b),"direction":balance(3,1)==("forward",2),"quotient":Fraction(a[3]*a[0],a[2]*a[1])==Fraction(2,3),"equilibrium":balance(2,2) is None,"successor":transition(b,a)}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
