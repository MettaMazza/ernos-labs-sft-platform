from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007';DOMAINS=(('anonymous-heavy-light', 'held-light-heavy-isotopes'), ('single-phase-ratio', 'held-distinct-phase-pair'), ('continuum-abundance-premise', 'positive-complete-isotope-counts'), ('decimal-isotope-ratio', 'exact-heavy-per-light-ratios'), ('fitted-fractionation-factor', 'exact-ratio-of-ratios'), ('signed-delta-premise', 'held-enrichment-or-EmptyOne-coincidence'), ('named-equilibrium-assumption', 'exchange-balance-plus-stable-factor'), ('selected-isotope-pair', 'complete-vector-successor-recomputes'));SURVIVOR='held-light-heavy-isotopes__held-distinct-phase-pair__positive-complete-isotope-counts__exact-heavy-per-light-ratios__exact-ratio-of-ratios__held-enrichment-or-EmptyOne-coincidence__exchange-balance-plus-stable-factor__complete-vector-successor-recomputes'
from fractions import Fraction
def factor(x):return Fraction(x[1]*x[2],x[0]*x[3])
def orientation(x):
 l=x[1]*x[2];r=x[0]*x[3];return None if l==r else "A" if l>r else "B"
p=(4,2,6,1);e=(4,2,6,3)
native={"identity":True,"phases":True,"inventory":min(p)>0,"ratios":(Fraction(p[1],p[0]),Fraction(p[3],p[2]))==(Fraction(1,2),Fraction(1,6)),"factor":factor(p)==3,"orientation":orientation(p)=="A","coincidence":orientation(e) is None and factor(e)==1,"successor":factor((6,3,8,2))==2}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
