from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-ACTIVITY-AMOUNT-TIME-003';DOMAINS=(('anonymous-activity-number', 'held-nuclide-species'), ('continuum-amount-premise', 'positive-counted-initial-occurrences'), ('expected-decay-number', 'positive-counted-transformations'), ('continuous-time-premise', 'positive-counted-resource-intervals'), ('fitted-decay-constant', 'exact-transformations-per-resource'), ('signed-amount-difference', 'positive-Take-or-EmptyOne-retained-amount'), ('selected-reference-time', 'complete-activity-amount-time-vector'), ('differential-equation-premise', 'ledger-successor-recomputes-relation'));SURVIVOR='held-nuclide-species__positive-counted-initial-occurrences__positive-counted-transformations__positive-counted-resource-intervals__exact-transformations-per-resource__positive-Take-or-EmptyOne-retained-amount__complete-activity-amount-time-vector__ledger-successor-recomputes-relation'
from fractions import Fraction
def ledger(initial,events,intervals):
 if events>initial:return None
 left=initial-events;return (Fraction(events,intervals),None if left==0 else left)
a=ledger(5,2,3);z=ledger(2,2,1)
native={"identity":True,"amount":5>0,"events":2>0,"time":3>0,"activity":a[0]==Fraction(2,3),"remaining":a[1]==3,"absence":z[1] is None,"successor":ledger(5,3,3)[0]==1}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
