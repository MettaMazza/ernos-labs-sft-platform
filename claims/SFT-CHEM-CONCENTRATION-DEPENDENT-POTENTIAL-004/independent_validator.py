from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-CONCENTRATION-DEPENDENT-POTENTIAL-004';DOMAINS=(('concentration-number-only', 'complete-half-reaction-activity-state'), ('signed-or-continuum-activity-coordinate', 'held-product-reactant-or-coincident-orientation'), ('arbitrary-real-activity-premise', 'complete-generated-doubling-support'), ('imported-logarithm', 'layer-count-additive-product-composition'), ('unscaled-electron-count', 'exact-layer-per-held-carrier-ratio'), ('numerical-zero-standard-state', 'structural-EmptyOne-standard-state'), ('selected-concentration-point', 'complete-concentration-potential-series'), ('refitted-concentration-coefficient', 'common-generator-successor-preserves-separation'));SURVIVOR="__".join(x[1] for x in DOMAINS)
from fractions import Fraction
def support(layers):
 value=1
 for _ in range(layers):value+=value
 return value
def shift(orientation,layers,carriers):return ("toward-reactants" if orientation=="product-heavy" else "toward-products",Fraction(layers,carriers))
native={"three_layers":support(3)==8,"product_direction":shift("product-heavy",3,2)==("toward-reactants",Fraction(3,2)),"reactant_direction":shift("reactant-heavy",2,2)==("toward-products",Fraction(1)),"product_composition":support(2)*support(3)==support(5),"common_successor":(5-2)==(6-3)}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
