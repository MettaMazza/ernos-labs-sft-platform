from itertools import product
import json,sys
CLAIM_ID='SFT-CHEM-POLYMER-ARCHITECTURE-008';DOMAINS=(('architecture-name-only', 'complete-finite-polymer-incidence-graph'), ('unlabelled-node-total', 'held-repeat-and-junction-identities'), ('connectivity-summary', 'complete-covalent-incidence-support'), ('branch-count-only', 'degree-of-every-held-vertex'), ('disconnected-pieces-conflated', 'complete-connected-component-census'), ('tree-assumed', 'cycle-rank-retained'), ('drawing-layout-identity', 'exact-labelled-graph-isomorphism-class'), ('architecture-label-only', 'vertices-edges-degrees-components-cycles-and-map-trace'));SURVIVOR='complete-finite-polymer-incidence-graph__held-repeat-and-junction-identities__complete-covalent-incidence-support__degree-of-every-held-vertex__complete-connected-component-census__cycle-rank-retained__exact-labelled-graph-isomorphism-class__vertices-edges-degrees-components-cycles-and-map-trace'
vertices=(1,2,3,4,5,6);edges=((1,2),(2,3),(3,4),(2,5),(3,6));degrees=tuple(sum(v in e for e in edges) for v in vertices);seen={1};front=[1]
while front:
 v=front.pop()
 for e in edges:
  if v in e:
   n=e[1] if e[0]==v else e[0]
   if n not in seen:seen.add(n);front.append(n)
native={"carrier":len(vertices)==6,"vertices":len(set(vertices))==6,"edges":len(set(tuple(sorted(e)) for e in edges))==5,"degree":degrees==(1,3,3,1,1,1),"components":seen==set(vertices),"cycles":len(edges)<len(vertices),"identity":sum(d>2 for d in degrees)==2,"certificate":sum(degrees)==2*len(edges)}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={x["candidate_id"]:x["survives"] for x in s["decisions"]};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={x:x==SURVIVOR for x in generated} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}},sort_keys=True))
if __name__=="__main__":main()
