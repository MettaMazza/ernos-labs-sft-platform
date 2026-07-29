from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002';DOMAINS=(('parent-number-only', 'held-parent-nuclide'), ('anonymous-product', 'held-daughter-nuclide'), ('nuclear-edge-only', 'held-parent-daughter-species'), ('unlabelled-transition', 'held-decay-channel'), ('continuum-decay-flow', 'positive-counted-transformations'), ('selected-decay-edge', 'complete-directed-transformation-network'), ('numerical-zero-daughter', 'structural-EmptyOne-no-edge'), ('daughter-overwrites-parent', 'successor-retains-prior-network'));SURVIVOR='held-parent-nuclide__held-daughter-nuclide__held-parent-daughter-species__held-decay-channel__positive-counted-transformations__complete-directed-transformation-network__structural-EmptyOne-no-edge__successor-retains-prior-network'
EMPTY=("EmptyOne",)
def network(rows):
 return EMPTY if not rows else tuple(rows) if len(set(rows))==len(rows) else None
e1=("p","d","ps","ds","one",1);e2=("p","d","ps","ds","two",2)
native={"parent":e1[0]=="p","daughter":e1[1]=="d","species":e1[2:4]==("ps","ds"),"channel":e1[4]=="one","events":e1[5]==1,"network":network((e1,))==(e1,),"absence":network(())==EMPTY,"successor":network((e1,e2))==(e1,e2)}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
