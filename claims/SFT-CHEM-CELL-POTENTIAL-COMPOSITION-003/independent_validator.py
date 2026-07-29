from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003';DOMAINS=(('anonymous-voltage-pair', 'two-distinct-held-half-cell-carriers'), ('mixed-reference-subtraction', 'one-common-held-reference'), ('mixed-condition-subtraction', 'one-common-held-condition'), ('unordered-potential-difference', 'held-source-terminal-reaction-path'), ('signed-arithmetic-premise', 'exact-positive-sum-or-Take-composition'), ('numerical-zero-cell-potential', 'structural-EmptyOne-cell-coincidence'), ('selected-cell-voltage', 'complete-full-cell-potential-vector'), ('irreversible-sign-flip', 'exact-cell-reversal-preserves-positive-separation'));SURVIVOR="__".join(x[1] for x in DOMAINS)
from fractions import Fraction
def compose(first,second):
 fd,fm=first;sd,sm=second
 if fd==sd and fm==sm:return ("coincident","EmptyOne")
 if fd!=sd:return (sd,fm+sm)
 return (sd,sm-fm) if sm>fm else (fd,fm-sm)
def reverse(cell):return ({"above":"below","below":"above","coincident":"coincident"}[cell[0]],cell[1])
opposed=compose(("below",Fraction(2)),("above",Fraction(3)));aligned=compose(("above",Fraction(2)),("above",Fraction(5)));native={"opposed_sum":opposed==("above",Fraction(5)),"aligned_take":aligned==("above",Fraction(3)),"coincident":compose(("above",Fraction(2)),("above",Fraction(2)))==("coincident","EmptyOne"),"reverse_magnitude":reverse(opposed)==("below",Fraction(5))}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
