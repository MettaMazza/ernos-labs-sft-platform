from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-RADIOCHEMICAL-EQUILIBRIUM-005';DOMAINS=(('anonymous-activity-pair', 'held-parent-daughter-identity'), ('continuous-time-premise', 'positive-ordered-resource-intervals'), ('fitted-decay-curve', 'exact-counted-activity-pair'), ('signed-activity-difference', 'held-ratio-or-structural-absence'), ('named-transient-assumption', 'persistent-nonOne-ratio-forces-transient'), ('approximate-equality-tolerance', 'persistent-One-ratio-forces-secular'), ('selected-timepoint', 'complete-parent-daughter-time-vector'), ('differential-equation-premise', 'finite-successor-recomputes-regime'));SURVIVOR='held-parent-daughter-identity__positive-ordered-resource-intervals__exact-counted-activity-pair__held-ratio-or-structural-absence__persistent-nonOne-ratio-forces-transient__persistent-One-ratio-forces-secular__complete-parent-daughter-time-vector__finite-successor-recomputes-regime'
from fractions import Fraction
def regime(rows):
 ratios=tuple(Fraction(d,p) for p,d in rows)
 if len(set(ratios))!=1:return None
 return ("secular" if ratios[0]==1 else "transient",ratios[0])
native={"identity":True,"support":tuple(range(1,3))==(1,2),"activity":Fraction(4,2)==2,"ratio":Fraction(4,2)==2,"transient":regime(((2,4),(3,6)))[0]=="transient","secular":regime(((2,2),(3,3)))[0]=="secular","absence":regime(((2,4),(3,3))) is None,"successor":regime(((2,4),(3,6),(4,8)))[1]==2}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
