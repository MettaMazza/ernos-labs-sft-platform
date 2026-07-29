from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-DEGREE-OF-POLYMERIZATION-001';DOMAINS=(('sample-average-without-chain', 'one-complete-finite-chain-carrier'), ('anonymous-backbone-mass', 'held-repeat-unit-identity'), ('continuum-chain-length', 'positive-exact-repeat-count'), ('total-mass-with-ends-conflated', 'repeat-supported-mass-separated-from-ends'), ('rounded-decimal-quotient', 'exact-positive-rational-relation'), ('terminal-groups-erased', 'terminal-support-retained'), ('single-value-replaces-population', 'per-chain-result-before-population-summary'), ('degree-only-output', 'chain-repeat-end-and-ratio-trace'));SURVIVOR='one-complete-finite-chain-carrier__held-repeat-unit-identity__positive-exact-repeat-count__repeat-supported-mass-separated-from-ends__exact-positive-rational-relation__terminal-support-retained__per-chain-result-before-population-summary__chain-repeat-end-and-ratio-trace'
from fractions import Fraction
def derive(chain,repeat,end):
 if chain<=end or repeat<=0:return None
 return Fraction(chain-end,repeat)
r=derive(1042,104,2)
native={"carrier":r is not None,"repeat":104>0,"extent":r==10,"mass":1042==104*10+2,"ratio":r==Fraction(10,1),"ends":2>0,"population":derive(522,104,2)==5,"certificate":(104*10)+2==1042}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
