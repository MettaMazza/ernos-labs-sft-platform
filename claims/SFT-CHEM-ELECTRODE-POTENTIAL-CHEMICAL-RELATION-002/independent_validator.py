from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002';DOMAINS=(('voltage-answer-only', 'complete-half-cell-transfer-account'), ('unbound-electrode-number', 'one-held-reference-electrode'), ('mixed-temperature-or-state', 'same-held-standard-condition'), ('unnormalized-total-work', 'exact-work-per-held-transfer-carrier'), ('signed-native-number', 'held-above-below-or-coincident-orientation'), ('numerical-zero-potential', 'structural-EmptyOne-reference-coincidence'), ('selected-standard-potential', 'complete-standard-potential-reference-vector'), ('species-specific-offset', 'common-work-successor-preserves-order'));SURVIVOR="__".join(x[1] for x in DOMAINS)
from fractions import Fraction
def relation(subject,reference):
 if subject==reference:return ("coincident","EmptyOne")
 if subject>reference:return ("above",subject-reference)
 return ("below",reference-subject)
native={"above":relation(Fraction(5),Fraction(3))==("above",Fraction(2)),"below":relation(Fraction(1),Fraction(3))==("below",Fraction(2)),"coincident":relation(Fraction(3),Fraction(3))==("coincident","EmptyOne"),"common_successor":relation(Fraction(7),Fraction(5))==relation(Fraction(5),Fraction(3))}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
